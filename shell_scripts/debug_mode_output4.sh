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
        echo 'dvbs2rmt debug 9'
        sleep 0.1
        echo 'skew debug 10'
    else
        sleep 0.1
        echo 'skew debug off'
        sleep 0.1
        echo 'dvbs2rmt debug off'
        sleep 0.1
        echo 'console timestamp off'
        exit
    fi

    sleep $3
    echo 'skew debug off'
    sleep 0.1
    echo 'dvbs2rmt debug off'
    sleep 0.1
    echo 'console timestamp off'
    sleep 0.1
    echo 'sh 4 off'
    echo exit
} |
    if [[ $4 == 'on' ]]; then
        dt=$(date '+%d_%m_%Y_%H_%M_%S');
        telnet 0 $1 | tee /tmp/log/tpa/$2_output4_$dt.log
    else
        telnet 0 $1
    fi
