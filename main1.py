import cv2
from ultralytics import YOLO
import threading
import time
from datetime import datetime
import logging
import os
import numpy as np
import requests
import logging
import mysql.connector
import sys
import ast


RTSP_CCTV  = os.getenv("RTSP_CCTV", "rtsp://aintpjmto:aintp123!@172.150.150.3:554/Streaming/Channels/101")
DELAY_DETECTION = int(os.getenv("DELAY_DETECTION", "10"))
nocctv = os.getenv("nocctv", "01")
masking  = os.getenv("MASKING_CCTV", "((160, 1894), (169, 335), (9, 334), (8, 4), (170, 4))")
#masking = "((160, 1894), (169, 335), (9, 334), (8, 4), (170, 4))"
print(masking)
print(type(masking))
try:
    # Convert the string to a tuple
    masking1 = ast.literal_eval(masking)
    print(masking1)
    print(type(masking1))
except (SyntaxError, ValueError) as e:
    print(f"Error: {e}")

## DB CONNECTION
#model = YOLO(os.environ['MODEL'])
# user_db=os.environ['USER_DB']
# password_db=os.environ['PASSWORD_DB']
# host_db=os.environ['HOST_DB']
# database_db=os.environ['DATABASE']

#user_db = config.get("myvars", "USER_DB")

user_db = os.getenv("USER_DB", "gpu_server")
password_db = os.getenv("PASSWORD_DB", "@jmt02023")
host_db  = os.getenv("HOST_DB", "172.16.12.63")
database_db  = os.getenv("DATABASE", "ntp")

class_deteksi=""

#inisialisasi logging
file_handler = logging.FileHandler(filename='./log_server.log')
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

    logging.info("START TO VOICE OUTPUT NTP")
    #ENDPOINT=os.environ['ENDPOINT']
    ENDPOINT=os.getenv("ENDPOINT", "http://172.16.12.114:8200/status_auto")
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
        cap = cv2.VideoCapture(RTSP_CCTV)
        cur_dir = os.getcwd()
        model=YOLO("yolov8s.pt")
        get_fps = True
        get_fps_bis = True
        
        while cap.isOpened():
            success, frame_main = cap.read()
            if success:
                sound_thread = threading.Thread(target=play_sound)

                #frame=frame_main.copy()
                masking_frame=frame_main.copy()

                ## masking
                MaskCoord=np.array((masking1))
                cv2.fillPoly(masking_frame, pts=[MaskCoord], color=(0, 0, 0))
                #print(os)
                # cv2.imshow('CAM masking', masking_frame)
                # cv2.imshow('CAM LIVE', frame_main)
                
                ## mode max detection banyak
                results = model.track(masking_frame, persist=True, conf=0.60 , classes=[0,2,5], verbose=False, agnostic_nms=False)
                results2 = model.track(frame_main, persist=True, conf=0.60 , classes=[0,2,5], verbose=False, agnostic_nms=False)[0].plot(line_width=1, labels=True, conf=True)
                frame = results[0].plot(line_width=1, labels=True, conf=True)

                #cv2.imshow('CAM LIVE MASK', results2)

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
                            if int(time.time() - start_time_bis) == DELAY_DETECTION:
                                flag_bis=1
                                vid_writer_bis.release()
                                get_fps_bis = True
                                class_deteksi="bis"

                                file_name = datetime.now().strftime("%d%m%Y_%H:%M:%S")

                                #save pict
                                dir_pict_org=str(cur_dir)+"/image/IMG"+"_"+nocctv+"_"+file_name+".jpg"
                                cv2.imwrite(dir_pict_org, frame_main)
                                os.chmod(dir_pict_org, 0o0777)

                                ## directory gambar
                                dir_pict_org="/image/IMG"+"_"+str(nocctv)+"_"+file_name+".jpg"

                                ## directory video
                                dir_vid_org="/video/VID"+"_"+str(nocctv)+"_"+file_name+".mp4"
                                
                                #Inisialisasi mysql
                                try:
                                    cnx=mysql.connector.connect(
                                        user=user_db,
                                        password=password_db,
                                        host=host_db,
                                        database=database_db
                                    )

                                    if cnx.is_connected():
                                        logging.info("DATABASE CONNECTED TO NTP")

                                except:
                                    logging.info("DATABASE NOT CONNEDTED TO NTP")

                                ## insert mysql
                                sql_insert="""INSERT INTO event (id_cctv,url_image,url_video,class,detection_object) VALUES(%s,%s,%s,%s,%s);"""
                                query_insert=(nocctv,dir_pict_org,dir_vid_org,class_deteksi,ntp_count)
                                
                                try:
                                    cursor=cnx.cursor()
                                    logging.info("START INSERTING TO MYSQL")
                                    cursor.execute(sql_insert,query_insert)
                                    cnx.commit()
                                    logging.info("SUCCESSED INSERTING TO MYSQL")
                                except:
                                    logging.error("NOT INSERTED TO DATABASE")
                                
                                cnx.close()

                                logging.info("END PROCESS RECORDING FRAME BIS")
                                logging.info("FLAG BIS SUDAH MENJADI 1 KEMBALI")

                            if int(time.time() - start_time_bis) > DELAY_DETECTION:
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

                        try:
                            logging.info("TEMP_ID: "+str(temp_id)+" CLASS_ID: "+str(id_box)+" FLAG:"+str(flag))
                        except:
                            pass

                        id_box=results[0].boxes.data.tolist()[0][4]

                        if id_box!= temp_id and flag==1: 

                            logging.info("ADA DETEKSI ORANG")
                            sound_thread.start()        
                            flag=0
                            start_time = time.time()
                            class_deteksi="orang"
                            file_name = datetime.now().strftime("%d%m%Y_%H:%M:%S")
                            
                            ## save pict
                            dir_pict_org=str(cur_dir)+"/image/IMG"+"_"+nocctv+"_"+file_name+".jpg"
                            cv2.imwrite(dir_pict_org, frame_main)

                            ## Inisialisasi mysql
                            try:
                                cnx=mysql.connector.connect(
                                    user=user_db,
                                    password=password_db,
                                    host=host_db,
                                    database=database_db
                                )

                                if cnx.is_connected():
                                    logging.info("DATABASE CONNECTED TO NTP")

                            except:
                                logging.info("DATABASE NOT CONNEDTED TO NTP")
                            
                            ## directory gambar
                            dir_pict_org="/image/IMG"+"_"+str(nocctv)+"_"+file_name+".jpg"

                            ## directory video
                            dir_vid_org="/video/VID"+"_"+str(nocctv)+"_"+file_name+".mp4"
                            
                            ## insert mysql
                            sql_insert="""INSERT INTO event (id_cctv,url_image,url_video,class,detection_object) VALUES(%s,%s,%s,%s,%s);"""
                            query_insert=(nocctv,dir_pict_org,dir_vid_org,class_deteksi,ntp_count)
                            
                            try:
                                cursor=cnx.cursor()
                                logging.info("START INSERTING TO MYSQL")
                                cursor.execute(sql_insert,query_insert)
                                cnx.commit()
                                logging.info("SUCCESSED INSERTING TO MYSQL")
                            except:
                                logging.error("NOT INSERTED TO DATABASE")
                            
                            cnx.close()

                            logging.info("END TO INSERT MYSQL")
                            logging.info("FLAG DETEKSI ORANG "+str(flag))

                        if int(time.time() - start_time) == DELAY_DETECTION:
                            flag=1
                            vid_writer.release()
                            get_fps = True
                            
                            logging.info("END PROCESS RECORDING FRAME ORANG")
                            logging.info("FLAG ORANG SUDAH MENJADI 1 KEMBALI")

                        if int(time.time() - start_time) > DELAY_DETECTION:
                            flag=1
                            vid_writer.release()
                            get_fps = True

                            logging.info("END PROCESS RECORDING FRAME ORANG")
                            logging.info("FLAG ORANG SUDAH MENJADI 1 KEMBALI")

                        temp_id=id_box

                ## RECORDING ORANG
                try:    
                    if flag==0 and int(time.time() - start_time) <= DELAY_DETECTION:
                        if get_fps == True:
                            logging.info("STARTING TO CAPTURE PROGRAM FRAME ORANG")
                            get_fps = False

                            ## get fps dan resolusi video bis
                            fps = cap.get(cv2.CAP_PROP_FPS)
                            h, w, c = frame_main.shape
                            
                            ## save pict orang
                            ## dir_pict_org=str(cur_dir)+"/image/IMG"+"_"+nocctv+"_"+file_name+".jpg"
                            ## cv2.imwrite(dir_pict_org, frame_main)

                            ## starting to vid
                            dir_vid_org="./video/VID"+"_"+str(nocctv)+"_"+file_name+".mp4"
                            vid_writer = cv2.VideoWriter(dir_vid_org, cv2.VideoWriter_fourcc(*'MJPG'), fps, (w, h))
                            logging.info("GET RECORDING FRAME ORANG")
                            

                        ## save vid output
                        vid_writer.write(frame_main)
                        logging.info("PROCESS RECORDING FRAME ORANG")
                        try:
                            logging.info(str(int(time.time() - start_time)))
                            logging.info("FLAG DETEKSI ORANG "+str(flag))
                        except:
                            pass
                except:
                    pass

                ## RECORDING BIS
                try:        
                    if flag_bis==0 and int(time.time() - start_time_bis) <= DELAY_DETECTION:
                        if get_fps_bis == True :
                            logging.info("STARTING TO CAPTURE PROGRAM FRAME BIS")
                            get_fps_bis = False

                            ## get fps dan resolusi video bis
                            fps = cap.get(cv2.CAP_PROP_FPS)
                            h, w, c = frame_main.shape
                            file_name = datetime.now().strftime("_%d%m%Y_%H:%M:%S")
                            class_deteksi="bis"

                            ## save pict orang
                            ## dir_pict_org="/image/IMG"+"_"+nocctv+"_"+file_name+".jpg"
                            ## cv2.imwrite(dir_pict_org, frame_main)

                            ## starting to vid
                            dir_vid_org="./video/VID"+"_"+str(nocctv)+"_"+file_name+".mp4"
                            vid_writer_bis = cv2.VideoWriter(dir_vid_org, cv2.VideoWriter_fourcc(*'MJPG'), fps, (w, h))
                            logging.info("GET RECORDING FRAME ORANG")

                        ## output.write(frame)
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
        
