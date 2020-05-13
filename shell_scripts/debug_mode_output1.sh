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
        echo 'pcmd 1000 rmt list | grep ' $2 
        sleep 0.1
        echo 'pcmd 5000 rh ucp table'
        sleep 0.1
        echo 'pcmd 1000 qos status'
    else
        sleep 0.1
        echo 'pcmd clear'
        sleep 0.1
        echo 'console timestamp off'
        exit
        echo 'sh 1 off'
    fi

    sleep $3
    echo 'pcmd clear'
    sleep 0.1
    echo 'console timestamp off'
    sleep 0.1
    echo exit
} |
    if [[ $4 == 'on' ]]; then
        dt=$(date '+%d_%m_%Y_%H_%M_%S');

        telnet 0 $1 | tee /tmp/log/tpa/$2_output1_$dt.log
    else
        telnet 0 $1
    fi
