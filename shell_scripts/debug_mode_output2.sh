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
        echo 'pcmd 5000 qos params'
        sleep 0.1
        echo 'bs_debug 10'
    else
        sleep 0.1
        echo 'bs_debug off'
        sleep 0.1
        echo 'pcmd clear'
        sleep 0.1
        echo 'console timestamp off'
        exit
    fi

    sleep $3
    echo 'bs_debug off'
    sleep 0.1
    echo 'pcmd clear'
    sleep 0.1
    echo 'console timestamp off'
    sleep 0.1
    echo 'sh 2 off'
    echo exit
} |
    if [[ $4 == 'on' ]]; then
        dt=$(date '+%d_%m_%Y_%H_%M_%S');

        telnet 0 $1 | tee /tmp/log/tpa/$2_output2_$dt.log
    else
        telnet 0 $1
    fi
