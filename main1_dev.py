import cv2
from ultralytics import YOLO
import threading
from queue import Queue
# from playsound import playsound
import time
from datetime import datetime
import logging
import os
import numpy as np
import requests
import logging
# import influxdb_client
# from influxdb_client import InfluxDBClient, Point, WritePrecision
# from influxdb_client.client.write_api import SYNCHRONOUS
import mysql.connector
import sys


model = YOLO('yolov8s.pt')
nocctv=1

#inisialisasi logging
file_handler = logging.FileHandler(filename='log_ip.log')
stdout_handler = logging.StreamHandler(stream=sys.stdout)
handlers = [file_handler, stdout_handler]

logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s [%(levelname)s] - %(message)s',
    handlers=handlers,
    datefmt="%m/%d/%Y %H:%M:%S",
)
logger = logging.getLogger('LOGGER_NAME')





def play_sound():
    #program sound from server itself
    # filename = 'sound.wav'
    # time.sleep(2)
    # playsound(filename)
    logging.info("START TO VOICE OUTPUT NTP")
    ENDPOINT="http://172.16.12.114:8200/status_auto"
    r = requests.get(url = ENDPOINT)
    data = r.json()
    pesan=data['status']
    logging.warning(pesan)


if __name__ == '__main__':
        logging.info("START PROGRAM NTP")
        temp_id=0
        temp_id_bis=0
        flag=1
        flag_bis=1

        ## Inisialisasi cctv
        cap = cv2.VideoCapture("rtsp://aintpjmto:aintp123!@172.150.150.3:554/Streaming/Channels/101")

        #Inisialisasi mysql
        try:
            cnx=mysql.connector.connect(
                user="gpu_server",
                password="@jmt02023",
                host="172.16.12.63",
                database="ntp"
            )

        except:
            logging.info("DATABASE NOT CONNEDTED TO NTP")
        
        sound_file = 'sound.wav'
        
        get_fps = True
        get_fps_bis = True
        
        while cap.isOpened():
            success, frame_main = cap.read()
            if success:
                sound_thread = threading.Thread(target=play_sound)

                #frame=frame_main.copy()
                masking_frame=frame_main.copy()

                #masking
                MaskCoord=np.array(((3,714),(224,303),(1027,311),(1264,715),(1269,12),(13,18)))
                cv2.fillPoly(masking_frame, pts=[MaskCoord], color=(255, 255, 255))
                cv2.imshow('CAM LIVE', frame_main)
                #cv2.imshow('CAM LIVE MASK', masking_frame)

                #mode max detection 1
                #results = model.track(frame, persist=True, conf=0.60 , classes=0, verbose=False, agnostic_nms=False, max_det=1)
                
                #mode max detection banyak
                results = model.track(masking_frame, persist=True, conf=0.60 , classes=[0,2, 3, 5, 7], verbose=False, agnostic_nms=False)
                results2 = model.track(frame_main, persist=True, conf=0.60 , classes=[0,2, 3, 5, 7], verbose=False, agnostic_nms=False)[0].plot(line_width=1, labels=True, conf=True)
                frame = results[0].plot(line_width=1, labels=True, conf=True)
                #cv2.imshow('CAM LIVE MASK', frame)
                cv2.imshow('CAM LIVE MASK', results2)

                if len(results[0].boxes.cls) > 0 :

                    bus=2 #car
                    person=0
                    if bus in results[0].boxes.cls.tolist():
                        deteksi_bis=0
                        id_box_bis=results[0].boxes.data.tolist()[0][4]

                        if flag_bis==1 and id_box_bis!= temp_id_bis:
                            logging.info("ADA DETEKSI BUS")
                            start_time_bis = time.time()
                            flag_bis=0
                            for i in results[0].boxes.cls.tolist():
                                if i == bus:
                                    deteksi_bis=deteksi_bis+1

                            ntp_count=len(results[0].boxes.cls.tolist())-deteksi_bis
                            logging.info("NTP COUNT MASUK IF BIS DETEKSI: "+str(ntp_count))

                        try:
                            if int(time.time() - start_time_bis) == 10:
                                flag_bis=1
                                vid_writer_bis.release()
                                get_fps_bis = True

                                logging.info("END PROCESS RECORDING FRAME BIS")
                                logging.info("FLAG BIS SUDAH MENJADI 1 KEMBALI")

                            if int(time.time() - start_time_bis) > 10:
                                flag_bis=1
                                vid_writer_bis.release()
                                get_fps_bis = True
                                
                                logging.info("END PROCESS RECORDING FRAME BIS")
                                logging.info("FLAG BIS SUDAH MENJADI 1 KEMBALI")
                        except:
                            pass

                        temp_id_bis=id_box_bis

                    if person in results[0].boxes.cls.tolist():
                        deteksi_bis=0
                        if bus in results[0].boxes.cls.tolist():
                            for i in results[0].boxes.cls.tolist():
                                if i == bus:
                                    deteksi_bis=deteksi_bis+1

                            ntp_count=len(results[0].boxes.cls.tolist())-deteksi_bis
                            logging.info("ntp count dengan bis: "+str(ntp_count))
                        elif bus not in results[0].boxes.cls.tolist():
                            ntp_count=len(results[0].boxes.cls.tolist())
                            logging.info("ntp count tanpa bis: "+str(ntp_count))

                        ############## KOMENTAR UNTUK DEVELOPMENT ######
                        # print(results[0].boxes.id)
                        # print(results[0].boxes.data.tolist()[0][4])
                        # print("################")
                    #     # try:
                    #     #     id_box=int(str(i.id.tolist())[1][0])
                    #     # except:
                    #     #     pass
                    #     temp=i.cls[0].item()
                        #class_id = results[0].names[i.cls[0].item()]
                        # cords = results[0].boxes.xyxy[0].tolist()
                        # cords = [round(x) for x in cords]
                        # conf = round(results[0].boxes.conf[0].item(), 2)
                        try:
                            #print("---")

                            # #print(str(i.id.tolist())[1][0])
                            # #print(str(i.id.tolist()))
                            # #print("data: "+str(i.data.tolist()))
                            # #print("Object type:", class_id)
                            # print("Coordinates:", cords)
                            # print("Probability:", conf)

                            logging.info("TEMP_ID: "+str(temp_id)+" CLASS_ID: "+str(id_box)+" FLAG:"+str(flag))
                            #print("---")
                        except:
                            pass

                        id_box=results[0].boxes.data.tolist()[0][4]

                        if id_box!= temp_id and flag==1: 
                            #CONNECT TO RASPBERRY
                            logging.info("ADA DETEKSI ORANG")
                            sound_thread.start()        
                            flag=0
                            start_time = time.time()

                            
                            logging.info("FLAG DETEKSI ORANG "+str(flag))

                        if int(time.time() - start_time) == 10:
                            flag=1
                            vid_writer.release()
                            get_fps = True
                            
                            logging.info("END PROCESS RECORDING FRAME ORANG")
                            logging.info("FLAG ORANG SUDAH MENJADI 1 KEMBALI")

                        if int(time.time() - start_time) > 10:
                            flag=1
                            vid_writer.release()
                            get_fps = True

                            logging.info("END PROCESS RECORDING FRAME ORANG")
                            logging.info("FLAG ORANG SUDAH MENJADI 1 KEMBALI")

                        temp_id=id_box

                #RECORDING ORANG
                try:    
                    if flag==0 and int(time.time() - start_time) <= 10:
                        if get_fps == True:
                            logging.info("STARTING TO CAPTURE PROGRAM FRAME ORANG")
                            get_fps = False

                            #get fps dan resolusi video bis
                            fps = cap.get(cv2.CAP_PROP_FPS)
                            h, w, c = frame_main.shape
                            file_name = datetime.now().strftime("_%d%m%Y_%H:%M:%S")

                            #save pict orang
                            cv2.imwrite("./image/IMG"+"_"+nocctv+"_"+file_name+".jpg", frame_main)

                            #starting to vid
                            #output = cv2.VideoWriter("./video/VID"+file_name+"-mpeg.avi", cv2.VideoWriter_fourcc(*'MPEG'), fps, (w, h))
                            vid_writer = cv2.VideoWriter("./video/VID"+"_"+nocctv+"_"+file_name+".avi", cv2.VideoWriter_fourcc(*'MJPG'), fps, (w, h))
                            logging.info("GET RECORDING FRAME ORANG")

                            #insert influxdb
                            logging.info("START TO INSERT INFLUX")

                            # token = "strVpIeCo9qEiZe3SGb_laqZlhJgDCXTDMI2ksZxVIROV-fTNizhqbO8PTJFRqG4_Bb_iJCc2nAOL-OpThZkyA=="
                            # org = "ntp"
                            # url_influx = "http://localhost:8086"

                            # write_client = influxdb_client.InfluxDBClient(url=url_influx, token=token, org=org)
                            # logger.info(write_client)
                            # write_api = write_client.write_api(write_options=SYNCHRONOUS)

                            # json_data = [
                            #     {
                            #         "measurement": "ntp1",  # Measurement name
                            #         "tags": {
                            #             "ip_location":"192.168.100.100",
                            #             "location": "KM99A",
                            #             "IMG": str("./image/IMG"+file_name+".jpg"),
                            #             "VID": str("./video/VID"+file_name+"-mjpg.avi"), 
                            #             "detection":"1",
                            #             "class":"0"      # Tags (optional)
                            #         },
                            #         "time": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),  # Timestamp in RFC3339 format (optional)
                            #         "fields": {
                            #             "pcount": int(ntp_count)           # Field(s)
                            #         }
                            #     }
                            # ]

                            # # Write the data to InfluxDB
                            # write_api.write(bucket='ntp', record=json_data)
                            # write_client.close()
                            logging.info("END TO INSERT INFLUX")

                        #save vid output
                        vid_writer.write(frame_main)
                        logging.info("PROCESS RECORDING FRAME ORANG")
                        try:
                            logging.info(str(int(time.time() - start_time)))
                            logging.info("FLAG DETEKSI ORANG "+str(flag))
                        except:
                            pass
                except:
                    pass

                #RECORDING BIS
                try:        
                    if flag_bis==0 and int(time.time() - start_time_bis) <= 10:
                        if get_fps_bis == True :
                            logging.info("STARTING TO CAPTURE PROGRAM FRAME BIS")
                            get_fps_bis = False

                            #get fps dan resolusi video bis
                            fps = cap.get(cv2.CAP_PROP_FPS)
                            h, w, c = frame_main.shape
                            file_name = datetime.now().strftime("_%d%m%Y_%H:%M:%S")

                            #save pict bis
                            logging.info("GET PICT FRAME BIS")
                            cv2.imwrite("./image/IMG_BIS"+"_"+nocctv+"_"+file_name+".jpg", frame_main)
                            
                            #starting to vid
                            logging.info("GET RECORDING FRAME BIS")
                            #output = cv2.VideoWriter("./video/VID_BIS"+file_name+"-mpeg.avi", cv2.VideoWriter_fourcc(*'MPEG'), fps, (w, h))
                            vid_writer_bis = cv2.VideoWriter("./video/VID_BIS"+"_"+nocctv+"_"+file_name+"-mjpg.avi", cv2.VideoWriter_fourcc(*'MJPG'), fps, (w, h))

                        #output.write(frame)
                        vid_writer_bis.write(frame_main)
                        logging.info("PROCESS RECORDING FRAME BIS")
                except:
                    logging.info("FLAG DETEKSI BIS "+str(flag_bis))
                    pass
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            else:
                break

        cap.release()
        cv2.destroyAllWindows()
        
