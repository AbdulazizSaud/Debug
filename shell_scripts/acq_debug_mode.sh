#!/bin/bash
{
    sleep 0.1
    echo $5
    sleep 0.1
    echo $6
    sleep 0.1
    if [[ $4 == 'on' ]]; then
        sleep 0.1
        echo 'console timestamp on'
        sleep 0.1
        echo 'net_debug 10'
        sleep 0.1
        echo 'enc_sess debug 9'
    else
        sleep 0.1
        echo 'pcmd clear'
        sleep 0.1
        echo 'net_debug off'
        sleep 0.1
        echo 'console timestamp off'
        sleep 0.1
        exit
        echo 'sh 1 off'
    fi

    sleep $3
    echo 'pcmd clear'
    sleep 0.1
    echo 'net_debug off'
    sleep 0.1
    echo 'console timestamp off'
    sleep 0.1
    echo exit
} |
    if [[ $4 == 'on' ]]; then
        dt=$(date '+%d_%m_%Y_%H_%M_%S');

        telnet 0 $1 | tee /tmp/log/acq/$2_$dt.log
    else
        telnet 0 $1
    fi
