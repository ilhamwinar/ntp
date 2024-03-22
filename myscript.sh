#!/bin/bash
#/usr/bin/env python3

export DISPLAY=:0 #needed if you are running a simple gui app.

cd "$(dirname "$0")"

process=script_ntp
while true
do

    if ! ps aux | grep -v grep | grep 'python3 main1_new.py --rtsp rtsp://admin:tahun2023 --rtsp2 @10.6.116.87:554/Streaming/Channels/101/ --delay 20 --nocctv 1' > /dev/null
    then #--nocctv 1
        python3 main1_new.py --rtsp rtsp://admin:tahun2023 --rtsp2 @10.6.116.87:554/Streaming/Channels/101/ --delay 20 --nocctv 1 --masking "((135, 201), (250, 210), (800, 800), (1280, 800), (1280, 0), (9, 0), (73, 175))" --input_titik KM_122_A --endpoint http://10.6.105.38:8200/status_auto &
        sleep 30 #--nocctv 1
    fi #--nocctv 1

    if ! ps aux | grep -v grep | grep 'python3 main1_new.py --rtsp rtsp://admin:tahun2023 --rtsp2 @10.6.116.88:554/Streaming/Channels/101/ --delay 20 --nocctv 2' > /dev/null
    then #--nocctv 2
        python3 main1_new.py --rtsp rtsp://admin:tahun2023 --rtsp2 @10.6.116.88:554/Streaming/Channels/101/ --delay 20 --nocctv 2 --masking "((674, 714), (1184, 186), (1274, 1), (0, 0), (0, 720))" --input_titik KM_127_A --endpoint http://10.6.105.39:8200/status_auto &
        sleep 30 #--nocctv 2
    fi #--nocctv 2


    if ! ps aux | grep -v grep | grep 'python3 main1_new.py --rtsp rtsp://admin:tahun2023 --rtsp2 @10.6.116.85:554/Streaming/Channels/101/ --delay 20 --nocctv 3' > /dev/null
    then #--nocctv 3
        python3 main1_new.py --rtsp rtsp://admin:tahun2023 --rtsp2 @10.6.116.85:554/Streaming/Channels/101/ --delay 20 --nocctv 3 --masking "((203, 698), (123, 312), (185, 306), (617, 720), (1280, 720), (1280, 0), (0, 0), (17, 699))" --input_titik KM_105_A --endpoint http://10.6.105.40:8200/status_auto &
        sleep 30 #--nocctv 3
    fi #--nocctv 3    

    if ! ps aux | grep -v grep | grep 'python3 main1_new.py --rtsp rtsp://admin:tahun2023 --rtsp2 @10.6.116.86:554/Streaming/Channels/101/ --delay 20 --nocctv 4' > /dev/null
    then #--nocctv 4
        python3 main1_new.py --rtsp rtsp://admin:tahun2023 --rtsp2 @10.6.116.86:554/Streaming/Channels/101/ --delay 20 --nocctv 4 --masking "((0, 0), (0, 720), (150, 720), (120, 180), (181, 180), (605, 720), (1280, 720), (1280, 0))" --input_titik KM_122_B --endpoint http://10.6.105.37:8200/status_auto &
        sleep 30 #--nocctv 4
    fi #--nocctv 4

sleep 10
done
exit
        