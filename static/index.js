$(document).ready(function () {
    var PPobj;
    var xmlPPServices = new XMLHttpRequest();

    xmlPPServices.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {

            response = JSON.parse(this.responseText)

            if (response == 'wait') {
                $('#serversTable').append('Watting to load .. ');
                return;
            }

            PPobj = response['data']
            i = 1
            count = 0
        
            for (var key in PPobj) {
                if (PPobj.hasOwnProperty(key)) {

                    if (PPobj[key]['isSuccessful'] == "false") {
                        

                        if(count == 0){
                            tag_start = `
                            <tr align=\"center\" > 
                            <th rowspan="2"> ${i} </th> 
                            <td> ${key.replace('Beam', '')} </td> 
                            <td> - </td>
                            <td> - </td>
                            <td> - </td>
                            </tr>
                            `
                            $('#serversTable').append(tag_start)
                            count++
        
                            } else {
                                tag_start = `
                                <tr align=\"center\" > 
                                <td> ${key.replace('Beam', '')} </td> 
                                <td> - </td>
                                <td> - </td>
                                <td> - </td>
                                </tr>
                                `
                                $('#serversTable').append(tag_start)
                                count=0
                                i++
        
                            }

                        continue;
                    } 

                    data = PPobj[key]['results']
                    ACQ_IP = data['PP_ACQ']['acq_rx_addr'].split(';')[1]
                    ACQ_PORT = data['PP_ACQ']['port']

                    NA_IP = data['PP_NA']['na_mnc_addr'].split(';')[1]
                    NA_PORT = data['PP_NA']['port']

                    DA_IP = data['PP_DA']['da_mnc_addr'].split(';')[1]
                    DA_PORT = data['PP_DA']['port']


    
                    if(count == 0){
                    tag_start = `
                    <tr align=\"center\" > 
                    <th rowspan="2"> ${i} </th> 
                    <td> ${key.replace('Beam', '')} </td> 
                    <td> ${ACQ_IP}:${ACQ_PORT} </td>
                    <td>${NA_IP}:${NA_PORT} </td>
                    <td>${DA_IP} : ${DA_PORT }</td> 
                    </tr>
                    `
                    $('#serversTable').append(tag_start)
                    count++

                    } else {
                        tag_start = `
                        <tr align=\"center\" > 
                        <td> ${key.replace('Beam', '')} </td> 
                        <td> ${ACQ_IP}:${ACQ_PORT} </td>
                        <td>${NA_IP}:${NA_PORT} </td>
                        <td>${DA_IP} : ${DA_PORT }</td> 
                        </tr>
                        `
                        $('#serversTable').append(tag_start)
                        count=0
                        i++

                    }

                    
                }
            }


        }
    };
    xmlPPServices.open("POST", "getPPServices", true);
    xmlPPServices.send();





    var xmlTPA = new XMLHttpRequest();

    xmlTPA.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {


            response = JSON.parse(this.responseText)

            if (response == 'wait')
                return;

            var loggingResponseData = response['info']['data']
            var active_debug = response['on']

 


            for (var server in loggingResponseData) {
                results = loggingResponseData[server]['results']


                for (var key in results) {
                    if (results.hasOwnProperty(key)) {
                        server_ip = server.replace(new RegExp("_", "g"),".")

                        data = results[key]
                        status = data['status'].split(" ")[0].replace('_', ' ')
                        time_split = data['status'].split(" ")
                        time_split.shift()
                        var status = data['status'].split(" ")[0].toUpperCase()
                        is_up = (status == 'IN_NETWORK')
                        var inet = data['beam']
                        var tail = data['tail']
                        var rf = data['rf']
                        console.log(rf)

                        passing_data = JSON.stringify({'cx':key,'parent_server':server_ip,'beam_info':PPobj['Beam'+inet]})
                        



                        time = ""
                        for (var col in time_split) {
                            time += time_split[col] + " "
                        }

                        isAcive = active_debug.hasOwnProperty(key)
                        time_pass = "00:00:00"

                        if(isAcive && is_up ){

                            var periods = {
                                month: 30 * 24 * 60 * 60 * 1000,
                                week: 7 * 24 * 60 * 60 * 1000,
                                day: 24 * 60 * 60 * 1000,
                                hour: 60 * 60 * 1000,
                                minute: 60 * 1000
                              };

                            get_time_ = (active_debug[key]['start_time']+'').split('.')
                            time_formated = get_time_[0]+get_time_[1][0]+get_time_[1][1]+get_time_[1][2]
                            time_start = parseInt(time_formated)
                            time_spent  = Date.now() - time_start

                            if (time_spent > periods.month) {
                                // it was at least a month ago
                                time_pass = Math.floor(time_spent / periods.month) + " min";
                              } else if (time_spent > periods.week) {
                                time_pass = Math.floor(time_spent / periods.week) + " week";
                              } else if (time_spent > periods.day) {
                                time_pass = Math.floor(time_spent / periods.day) + " day";
                              } else if (time_spent > periods.hour) {
                                time_pass = Math.floor(time_spent / periods.hour) + " hr";
                              } else if (time_spent > periods.minute) {
                                time_pass = Math.floor(time_spent / periods.minute) + " min";
                              } else {
                                time_pass = '<1min'
                              }

                        }
                        

                        beam_number = '-'
                        rate = '-'
                        out_freq = '-'
                        in_freq = '-'
                        power = '-'
                        ter_type = '-'

                        if(rf !== undefined){
                            beam_number = rf['beam']
                            rate = rf['rate']
                            in_freq = rf['in_freq']
                            out_freq = rf['out_freq']
                            ter_type = rf['ter_type']
                            power = rf['power'].replace('ChannelDetailsofSatelliteE70B:','')
                            


                        }

                        play_pause = (isAcive && is_up) ? 'pause' : 'play'

                        color = (status == 'IN_NETWORK') ? 'rgb(0, 226, 0)' : 'rgb(226, 0, 0)'
                        enabled = (status == 'IN_NETWORK') ? '' : 'disabled'


                        table = `
                                <tr>
                                <th scope = \"row\"> ${server_ip} </th>
                                <td> ${key} </td> 
                                <td> ${tail}  </td> 
                                <td>${beam_number}</td>
                                <td>${inet}</td>
                                <td>${ter_type}</td>
                                <td>${power}</td>
                                <td>${rate}</td>
                                <td>out_freq:${out_freq} <br> in_freq:${in_freq}</td>
                                <td  style=\"color: ${color};\"> ${status} </td>
                                <td>${time}</td>
                                <td>  <button id=\"playb\" value='${passing_data}' class='button ${play_pause} +' ${enabled} ></button </td>
                                <td id=\"time_${key}\"> ${time_pass}</td>
                                
                                </tr>
                                `



                        $('#TerminalTable').append(table)
                    }
                }

            }



        }
    };

    xmlTPA.open("POST", "getLogging", true);
    xmlTPA.send();


    $(document).on("click", "#playb", function () {


        data = $(this).val()
        dataJson = JSON.parse(data)
        cx = dataJson['cx']


        condition = $(this).attr('class').includes('pause')
        play_pause = (condition) ? 'button play' : 'button pause'
        default_time = (!condition)?  'Now' : '00:00:00'
        $(this).attr('class', play_pause);
        $('#time_'+cx).html(default_time) 
        request_debug(!condition, data)

    });


    function request_debug(run, data) {


        dataJson = JSON.parse(data)
        beam_info = dataJson['beam_info']['results']
        
        ACQ_IP = beam_info['PP_ACQ']['acq_rx_addr'].split(';')[1]
        ACQ_PORT = beam_info['PP_ACQ']['port']

        NA_IP = beam_info['PP_NA']['na_mnc_addr'].split(';')[1]
        NA_PORT = beam_info['PP_NA']['port']

        DA_IP = beam_info['PP_DA']['da_mnc_addr'].split(';')[1]
        DA_PORT = beam_info['PP_DA']['port']

        reformat_data= {
            'cx': dataJson['cx'],
            'parent_server':dataJson['parent_server'],
            'services':{
                'ACQ_IP':ACQ_IP+':'+ACQ_PORT,
                'NA_IP':NA_IP+':'+NA_PORT,
                'DA_IP':DA_IP+':'+DA_PORT
            }
        }


        var xmlDebug = new XMLHttpRequest();
        if (run == true) {


            xmlDebug.onreadystatechange = function () {
                if (this.readyState == 4 && this.status == 200) {

                    response = JSON.parse(this.responseText)
                }
            };



            xmlDebug.open("POST", "startDebug/" + JSON.stringify(reformat_data), true);
            xmlDebug.send();
        } else {

            xmlDebug.onreadystatechange = function () {
                if (this.readyState == 4 && this.status == 200) {

                    response = JSON.parse(this.responseText)
                    console.log(response)
                }
            };


            xmlDebug.open("POST", "stopDebug/" +  JSON.stringify(reformat_data), true);
            xmlDebug.send();

        }

    }


});





