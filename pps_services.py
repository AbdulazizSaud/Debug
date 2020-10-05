from pexpect import pxssh, spawn, EOF, run, EOF
import time
import re
import json
import requests
import colorama
import os
servers = ['10.4.11.5', '10.4.11.4', '10.4.11.3', '10.4.11.2', '10.4.11.1']
beams = [5101, 5102, 5103, 5104, 5105, 5106, 5107, 5108, 5109, 5133]

username = 'idirect'
password = 'iDirect'
telnet_username = 'admin'

mainpath = '/tmp/scripts'
scripts_path = mainpath+'/shell_scripts'

ftp_ip = 'root@172.20.0.110'



####################################################
tail_numbers = {}
rftermtype__numbers = {}
pulse_user = 'tsc-app'
pulse_password = 'Tsc@pp123!'
pulse_auth = (pulse_user, pulse_password)
API_MAIN_URL = 'http://10.1.10.110/api/2.0/config/'
API_IDIRECT_SATTLE = API_MAIN_URL+'satelliterouter?limit=0'
API_IDIRECT_TERMINAL = API_MAIN_URL+'terminal?limit=0'
API_IDIRECT_TERMINAL_TYPE = API_MAIN_URL + 'terminaltype?limit=0'

###################################################
channels_dir = {}
current_gsr_ip = None
###################################################


def tpaGetAllList(options=None):
    result = {}
    global tail_numbers
    global rftermtype__numbers

    ########## DON'T DELETE THIS ################
    tail_numbers, rftermtype__numbers = fetch_tail_numbers()
    #############################################

    for server in servers:
        server_key = server.replace('.', '_')
        data = loggingServices('list', server,options = options)
        result[server_key] = data

    result = append_beams(result)
    return result


def fetch_channels(conn):
    conn.sendline("./geo_mode.sh "+telnet_username+' '+password)
    conn.prompt()

    channels = conn.before.split('INET ID: ')
    del channels[0]

    for channel in channels:
        lines = channel.split('[pp_geo')[0].split('RF Terminal Type: ')
        ##########  INET INFO    ##########
        INET_info = lines[0].split(' ')
        INET = INET_info[0]
        beam = INET_info[4]
        rate = INET_info[9]
        out_freq = INET_info[11]
        in_freq = INET_info[15]
        rf_dir = {}

        del lines[0]
        for rf in lines:
            rf = rf.replace(' ', '').split('MaxRFPower:')
            rf_terminal_type = rf[0]
            rf_max_power = rf[1].replace('\n', '').replace('\r', '')
            rf_dir[rf_terminal_type] = rf_max_power
        if INET not in channels_dir:
            channels_dir[INET] = {'beam': beam, 'rate': rate,
                                  'out_freq': out_freq, 'in_freq': in_freq, 'rf': rf_dir}



############ the issue is over here ############


def append_beams(results):
    for server in results:
        data = results[server]['results']
        for dd_id in data:
            try:
                _data = data[str(dd_id)]
                dd_beam = _data['beam']
                terminal_type = rftermtype__numbers[dd_id]
                rf_data =  channels_dir[dd_beam]['rf']
                
                if terminal_type in rf_data:
                    _tmp = channels_dir[dd_beam]
                    #del _tmp['rf']
                    power = rf_data[terminal_type]
                    _tmp['power'] = power
                    _tmp['ter_type'] = terminal_type
                    results[server]['results'][dd_id]['rf'] = _tmp
                    continue

            except Exception as e:
                results[server]['results'][dd_id]['rf'] = channels_dir[dd_beam]
                print('--->',e)

    return results



def loggingServices(action, server, service_type=None, d_id=None, active_time=None,options=None):
    server_tmp = server if ":" not in server else server.split(':')[0]
    tpa_ssh = pxssh.pxssh(timeout=3600, encoding='utf-8')
    tpa_ssh.login(server_tmp, username, password)
    print("SSH session login sucessful with TPA Server")
    tpa_ssh.sendline('mkdir /tmp/log/tpa')
    tpa_ssh.prompt()

    tpa_ssh.sendline('cd '+scripts_path)
    tpa_ssh.prompt()

    if(' No such file or directory' in tpa_ssh.before):
        upload_shell_scripts(server, tpa_ssh)
        tpa_ssh.sendline('cd '+scripts_path)
        tpa_ssh.prompt()

    results = {}
    if(action == 'list'):
        fetch_channels(tpa_ssh)
        tpa_ssh.sendline("./didlist.sh "+str(10006) +
                         ' '+telnet_username+' '+password)
        tpa_ssh.prompt()
        dd_ids = tpa_ssh.before.split('CX')
        del dd_ids[0]
        if options is not None: 
            os.system(options)
        for id_info in dd_ids:
            id_info = id_info.lower()
            dd_id = id_info.split('(')[1].split(')')[0]
            dd_status = id_info.split('(')[2].split(')')[0]
            dd_beam = id_info.split('inet:')[1].split('(')[0]
            dd_beam = dd_beam.replace(' ', '')
            try:
                dd_tail = tail_numbers[dd_id]
            
            except Exception as e:
                #print('no tail number')
                dd_tail = '-'

            results[dd_id] = {'tail': dd_tail,
                              'beam': dd_beam, 'status': dd_status}

        tpa_ssh.logout()

    elif (service_type == 'TPA'):
        print(f"${action} debuging TPA")
        if options is not None: os.system(options)
        logging_tpa(tpa_ssh, action, d_id, active_time)
    elif (service_type == 'DA'):
        print(f"${action} debuging DA")
        print(server.split(":")[1], server)
        logging_da(tpa_ssh, action, d_id, server.split(":")[1], active_time)
    elif (service_type == 'ACQ'):
        print(f"${action} debuging ACQ")
        logging_acq(tpa_ssh, action, d_id, server.split(":")[1], active_time)
    elif (service_type == 'NA'):
        print(f"${action} debuging NA")
        logging_na(tpa_ssh, action, d_id, server.split(":")[1], active_time)

    return {'isSuccessful': "true", 'error': "", 'results': results}


def logging_tpa(conn, action, d_id, active_time):
    if (action == 'start_debug'):

        conn.sendline("./excute_debug_mode.sh "+str(10006)+" " +
                      str(d_id)+" "+str(active_time)+" on"+' '+telnet_username+' '+password)

        conn.logout()

    elif (action == 'stop_debug'):
        print('stop debugging')

        conn.sendline("./excute_debug_mode.sh "+str(10006)+" " +
                      str(d_id)+" "+str(active_time)+" off"+' '+telnet_username+' '+password)
        file_path = '/tmp/log/tpa'
        transferFilesToFTPServer(file_path, conn)

        conn.logout()


def logging_da(conn, action, d_id, port, active_time):
    if (action == 'start_debug'):
        conn.sendline("./da_debug_mode.sh "+port+" " +
                      str(d_id)+" "+str(active_time)+" on"+' '+telnet_username+' '+password)

        print("./da_debug_mode.sh "+port+" " +
              str(d_id)+" "+str(active_time)+" on"+' '+telnet_username+' '+password)
        conn.logout()

    elif (action == 'stop_debug'):
        print('stop debugging')

        conn.sendline("./da_debug_mode.sh "+port+" " +
                      str(d_id)+" "+str(active_time)+" off"+' '+telnet_username+' '+password)
        file_path = '/tmp/log/da'

        transferFilesToFTPServer(file_path, conn)
        conn.logout()


def logging_acq(conn, action, d_id, port, active_time):
    if (action == 'start_debug'):

        conn.sendline("./acq_debug_mode.sh "+port+" " +
                      str(d_id)+" "+str(active_time)+" on"+' '+telnet_username+' '+password)

        conn.logout()

    elif (action == 'stop_debug'):
        print('stop debugging')

        conn.sendline("./acq_debug_mode.sh "+port+" " +
                      str(d_id)+" "+str(active_time)+" off"+' '+telnet_username+' '+password)
        file_path = '/tmp/log/acq'

        transferFilesToFTPServer(file_path, conn)

        conn.logout()


def logging_na(conn, action, d_id, port, active_time):
    if (action == 'start_debug'):
        print('mewoo', port)
        print("./na_debug_mode.sh "+port+" " +
              str(d_id)+" "+str(active_time)+" on"+' '+telnet_username+' '+password)

        conn.sendline("./na_debug_mode.sh "+port+" " +
                      str(d_id)+" "+str(active_time)+" on"+' '+telnet_username+' '+password)
        conn.prompt()

        conn.logout()

    elif (action == 'stop_debug'):
        print('stop debugging')

        conn.sendline("./na_debug_mode.sh "+port+" " +
                      str(d_id)+" "+str(active_time)+" off"+' '+telnet_username+' '+password)
        file_path = '/tmp/log/na'

        transferFilesToFTPServer(file_path, conn)

        conn.logout()


def getPPServices(options=None):
    result = {}
    get_current_gsr()
    if(current_gsr_ip == None):
        return

    gsr_ssh = pxssh.pxssh(20, encoding='utf-8')
    gsr_ssh.login(current_gsr_ip, username, password)
    print("SSH session login successful")
    gsr_ssh.sendline('ps -ef | grep pp_gsr')
    gsr_ssh.prompt()
    if options is not None: 
        os.system(options)
    print(gsr_ssh.before)
    port = str(gsr_ssh.before).split(
        '-cp')[1].replace(" ", "").split("-")[0]
    gsr_ssh.sendline('cd '+scripts_path)
    gsr_ssh.prompt()

    for beam in beams:
        tmp = fetch_info(beam, gsr_ssh, port)
        result['Beam'+str(beam)] = tmp

    for server in servers:
        portsForServices = getPorts(server)

        ppNA = portsForServices['pp_na']
        for beam in ppNA:
            if len(result['Beam'+beam]['results']) != 0:
                result['Beam'+beam]['results']['PP_NA']['port'] = ppNA[beam]

        ppDA = portsForServices['pp_da']
        for beam in ppDA:
            if len(result['Beam'+beam]['results']) != 0:
                result['Beam'+beam]['results']['PP_DA']['port'] = ppDA[beam]

        ppACQ = portsForServices['pp_acq']
        for beam in ppACQ:
            if len(result['Beam'+beam]['results']) != 0:
                result['Beam'+beam]['results']['PP_ACQ']['port'] = ppACQ[beam]

    gsr_ssh.logout()
    return result


def getPorts(ip):

    commands = {'pp_na', 'pp_acq', 'pp_da'}
    ssh_port = pxssh.pxssh(20, encoding='utf-8')
    ssh_port.login(ip, username, password)
    print("PORT session successful")
    result = {}

    for command in commands:
        ssh_port.sendline('ps -ef | grep '+command)
        ssh_port.prompt()
        result[command] = {}
        try:
            splited_cp_array = str(ssh_port.before).split('-cp')
            del splited_cp_array[0]
            for port in splited_cp_array:
                inet = port.split('-net')[1].replace(" ", "").split("-")[0]

                port = port.replace(" ", "").split("-")[0]
                result[command][inet] = port

        except Exception as e:
            result.update({command: []})

    ssh_port.logout()
    return result


def fetch_info(beam, gsr_ssh, port):
    try:

        gsr_ssh.sendline("./retreive.sh "+port+" "+str(beam) +
                         ' '+telnet_username+' '+password)
        gsr_ssh.prompt()

        output = str(gsr_ssh.before).split('Options:')[1].split('[pp_gsr')[0]
        jsonOutput = json.loads(output)

        return {'isSuccessful': "true", 'error': "", 'results': jsonOutput}
    except Exception as e:
        print(str(e))
        return {'isSuccessful': "false", 'error': "No beam", 'results': {}}


def transferFilesToFTPServer(path, conn):
    print('uploading files')
    conn.sendline('scp -r '+path + ' '+ftp_ip+':/tmp')
    conn.expect(ftp_ip+'\'s password:', timeout=50)
    conn.sendline('$fTp@$a$#110')
    print('removing tmp files')
    conn.sendline('cd '+path)
    conn.prompt()
   # conn.sendline("rm -r -f *")
    #conn.prompt()


def upload_remove_all_scripts_from_servers(swap):
    for server in servers:
        ssh = pxssh.pxssh(timeout=3600, encoding='utf-8')
        ssh.login(server, username, password)
        if(swap == True):
            remove_shell_scripts(ssh)
        else:
            upload_shell_scripts(server, ssh)

        ssh.logout()


def remove_shell_scripts(connection):
    connection.sendline('rm -r /tmp/scripts')
    connection.prompt()


def upload_shell_scripts(server, connection):
    print('server ==>', server)
    connection.sendline('mkdir -p '+mainpath)
    connection.prompt()
    print('making')
    connection.sendline('mkdir -p '+'/tmp/log/tpa')
    connection.prompt()
    connection.sendline('mkdir -p '+'/tmp/log/acq')
    connection.prompt()
    connection.sendline('mkdir -p '+'/tmp/log/da')
    connection.prompt()
    connection.sendline('mkdir -p '+'/tmp/log/na')
    connection.prompt()
    print(connection.before)
    ip = username+'@'+server
    command = 'scp -r shell_scripts' + ' '+ip+':'+scripts_path
    print(command)
    child = spawn(command, timeout=3000, encoding='utf-8')
    child.expect(ip+'\'s password:', timeout=50)
    child.sendline(password)
    child.expect(EOF)
    connection.sendline('chmod -R 755 '+scripts_path)
    connection.prompt()
    print(connection.before)


def fetch_tail_numbers():
    tail_number_tmp = {}
    did_objects_id_tmp = {}

    tail_number_ter_type_tmp = {}
    rfterm_type_tmp = {}


    response_sattle = requests.get(API_IDIRECT_SATTLE, auth=pulse_auth)
    
    sattle_data = response_sattle.json()['data']
    for sattle in sattle_data:
        did = sattle['obj_attributes']['did']
        obj_id = str(sattle['obj_id'])
        did_objects_id_tmp[obj_id] = did


    response_terminal = requests.get(API_IDIRECT_TERMINAL, auth=pulse_auth)
    terminal_data = response_terminal.json()['data']


    for tail in terminal_data:
        obj_id = str(tail['obj_attributes']['coremodule_id'])
        tail_number = tail['obj_name']
        terminaltype_id = str(tail['obj_attributes']['terminaltype_id'])

        try:
            did = str(did_objects_id_tmp[obj_id])
        except Exception as e:
            tail_number_ter_type_tmp[did] = str(terminaltype_id)
            continue
        
            
        tail_number_tmp[did] = tail_number
        tail_number_ter_type_tmp[did] = str(terminaltype_id)

    response_terminal_type = requests.get(API_IDIRECT_TERMINAL_TYPE, auth=pulse_auth)
    terminal_data_type = response_terminal_type.json()['data']


    for tmp_did in tail_number_ter_type_tmp :
        terminal_id = tail_number_ter_type_tmp[tmp_did]
        try:
            for rf_type in terminal_data_type:
                obj_id = str(rf_type['obj_id'])
                
                if  terminal_id == obj_id:
                    rfterm_type_tmp[tmp_did] = str(rf_type['obj_attributes']['rftermtype'])
                    break



        except:
            continue

    
    return tail_number_tmp, rfterm_type_tmp



def get_current_gsr():
    global current_gsr_ip
    port = None
    for server in servers:
        ssh = pxssh.pxssh(timeout=3600, encoding='utf-8')
        ssh.login(server, username, password)
        try:
            print(server)
            ssh.sendline('ps -ef | grep pp_gsr')
            ssh.prompt()
            port = str(ssh.before).split(
        '-cp')[1].replace(" ", "").split("-")[0]
            current_gsr_ip = server
            return
        except:
            ssh.logout()
            continue

        ssh.logout()
        

print(fetch_tail_numbers())

#fetch_tail_numbers()

#tpaGetAllList()
#loggingServices(action='list',server = servers[0])
#loggingServices('stop_debug',servers[0],service_type='TPA',d_id=352323199,active_time=1000000000)

#upload_remove_all_scripts_from_servers(True)
#upload_remove_all_scripts_from_servers(False)
