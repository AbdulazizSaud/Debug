import time
from flask import render_template, Flask,request
import json
import pps_services      
import pymongo
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import threading
import os




####################################################
mongo_client = pymongo.MongoClient("mongodb://0.0.0.0:27017/")
ppDb = mongo_client["ppservers"]
col = ppDb["tmp"]
col_ter = ppDb['terminals']

app = Flask(__name__, template_folder='static')
app.config["DEBUG"] = True

pp_data_id = 'pp_data'
tpa_data_id = 'tpa_data'

debug_threads = {}
scheduler = BackgroundScheduler()




def thread_logging_service(action,server,service_type,cx,options=None):
    print(action)
    if action == 'start':
        print('starting debugging')
        mongoDebug = {'_id': cx, 'data':'ON', 'start_time': time.time()}
        if col_ter.find({'_id': cx}).limit(1).count()  == 0:
            col_ter.insert_one(mongoDebug)
        pps_services.loggingServices(service_type=service_type,action='start_debug',server=server,d_id=cx,active_time=900,options=options)
    elif action == 'stop':
        print('stop debugging')
        if col_ter.find({'_id': cx}).limit(1).count() > 0:
            col_ter.delete_one({'_id': cx})
        
        pps_services.loggingServices(service_type=service_type,action='stop_debug',server=server,d_id=cx,active_time=900,options=options,)
        



    


def thread_pp_serivces(options = None):
    PPresult = pps_services.getPPServices(options=options)

    mongoPPData = {
        '_id': pp_data_id,
        'data':PPresult }

    col.insert_one(mongoPPData)
    del debug_threads[pp_data_id]


def thread_logging_services(options = None):
    print('test=>','thread_logging_services')

    TPAList = pps_services.tpaGetAllList(options=options)
    mongoTPAData = {
        '_id': tpa_data_id,
        'data':TPAList 
        }
        
    col.insert_one(mongoTPAData)
    del debug_threads[tpa_data_id]





def thread_updating(options=None):
    print('---> updating')
    PPresult = pps_services.getPPServices(options=options)
    mongoPPData = {
        '_id': pp_data_id,
        'data':PPresult }

    col.delete_one({'_id': pp_data_id})    
    col.insert_one(mongoPPData)
    print('mewo')
    TPAList = pps_services.tpaGetAllList()
    mongoTPAData = {
        '_id': tpa_data_id,
        'data':TPAList 
        }
    col.delete_one({'_id': tpa_data_id})  
    col.insert_one(mongoTPAData)
    print('test')      
    del debug_threads['update_all']



def update():
    if('update_all' in debug_threads):
        print('its now updating')
        return

    x = threading.Thread(target=thread_updating)
    x.start()
    debug_threads['update_all'] = x
    




@app.route('/startDebug/<string:data>', methods=['POST'])
def startDebugRPC(data):
    
    dataJson = json.loads(data)
    cx = dataJson['cx']
    if cx in debug_threads:
        return {"error": "thread is already existed","isSuccessful": "false"}
    options = None
    initLogging('start',dataJson,options)
    debug_threads[cx] = cx

    return json.dumps({"error": "","isSuccessful": "true"})
    

@app.route('/stopDebug/<string:data>', methods=['POST'])
def stopDebugRPC(data):
    options = None
    dataJson = json.loads(data)
    cx = dataJson['cx']
    initLogging('stop',dataJson,options)
    if cx in debug_threads:
        return {"error": "thread is already existed","isSuccessful": "false"}
    debug_threads[cx] = cx

    return json.dumps({"error": "","isSuccessful": "true"})



def initLogging(action,data,options=None):
    cx = data['cx']
    parentIP = data['parent_server']
    services = data['services']
    print(action)
    
    tpa = threading.Thread(target=thread_logging_service, args=(action,parentIP,'TPA',cx,options,))
    tpa.start()

    acq = threading.Thread(target=thread_logging_service, args=(action,services['ACQ_IP'],'ACQ',cx,options,))
    acq.start()

    na = threading.Thread(target=thread_logging_service, args=(action,services['NA_IP'],'NA',cx,options,))
    na.start()

    da = threading.Thread(target=thread_logging_service, args=(action,services['DA_IP'],'DA',cx,options,))
    da.start()




@app.route('/getPPServices', methods=['POST'])
def getPPServices_RPC():
    result ={}
    if col.find({'_id': pp_data_id}).limit(1).count() > 0:
        PPresult = col.find_one({'_id':pp_data_id})
        options = str(request.args.get('options'))
        if options is not None: 
            os.system(options)
        result= PPresult
    else:
        
        if pp_data_id in debug_threads :
            print('test')
            return 'wait'

        th1 = threading.Thread(target=thread_pp_serivces,args=(options,))
        th1.start()
        debug_threads[pp_data_id] = th1
        return 'wait'
        


    return json.dumps(result)     




@app.route('/getLogging', methods=['POST'])
def getLogging_RPC():
    result ={}

    if col.find({'_id': tpa_data_id}).limit(1).count() >0:
        loggingList = col.find_one({'_id':tpa_data_id})
        active_debugging = col_ter.find({})
        data={}
        options = str(request.args.get('options'))
        if options is not None: 
            os.system(options)

        for data_tmp in active_debugging:
            print(active_debugging)
            data[data_tmp['_id']] = data_tmp


        result= {'on':data,'info':loggingList}
        if not bool(loggingList['data'])  :
         update()
    else:

        if tpa_data_id in debug_threads :
            return 'wait'

        options = str(request.args.get('options'))
        th1 = threading.Thread(target=thread_logging_services,args=(options,))
        th1.start()
        debug_threads[tpa_data_id] = th1
        return 'wait'


    return json.dumps(result)     


@app.route('/', methods=['GET'])
def home():
    return render_template("index.html")




update()
scheduler.add_job(func=update, trigger="interval", seconds=900,id='update')
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())
app.run(host='0.0.0.0',port=80,use_reloader=False)

