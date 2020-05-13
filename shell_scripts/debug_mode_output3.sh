#!/bin/bash
{
    sleep 0.1
    echo $5
    sleep 0.1
    echo $6
    sleep 0.1
    echo rmt $2
    if [[ $4 == 'on' ]]; then
        sleep 0.1
        echo 'console timestamp on'
        sleep 0.1
        echo 'loc_map debug 9'
        sleep 0.1
        echo 'rh ucp_debug 5'
    else
        sleep 0.1
        echo 'rh ucp_debug off'
        sleep 0.1
        echo 'loc_map debug off'
        sleep 0.1
        echo 'console timestamp off'
        exit
    fi

    sleep $3
    echo 'rh ucp_debug off'
    sleep 0.1
    echo 'loc_map debug off'
    sleep 0.1
    echo 'console timestamp off'
    sleep 0.1
    echo exit
    echo 'sh 3 off'
} |
    if [[ $4 == 'on' ]]; then
        dt=$(date '+%d_%m_%Y_%H_%M_%S');

        telnet 0 $1 | tee /tmp/log/tpa/$2_output3_$dt.log
    else
        telnet 0 $1
    fi
