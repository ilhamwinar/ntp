import cv2
from ultralytics import YOLO
import threading
from queue import Queue
from playsound import playsound
import time
from datetime import datetime
#import datetime
import logging
import os
import numpy as np

model = YOLO('yolov8s.pt')

def play_sound():
    filename = 'sound.wav'
    time.sleep(2)
    playsound(filename)

if __name__ == '__main__':
        temp_id=0
        flag=1
        state_recording=1
        #cap = cv2.VideoCapture("rtsp://admin:p@ssw0rd@173.16.17.2:554/Streaming/Channels/102")
        cap = cv2.VideoCapture(0)
        sound_file = 'sound.wav'
        get_fps = True
        while cap.isOpened():
            success, frame = cap.read()
            if success:
                sound_thread = threading.Thread(target=play_sound)
                
                # recording_thread.start()
                #cv2.rectangle(frame, (900,130), (1200, 250), (0,0,0), -1)
                #results = model.track(frame, persist=True, conf=0.60 , classes=0, verbose=False, agnostic_nms=False, max_det=1)
                results = model.track(frame, persist=True, conf=0.60 , classes=[0,67], verbose=False, agnostic_nms=False)
                frame = results[0].plot(line_width=1, labels=True, conf=True)

                masking_frame=frame.copy()
                #crop_frame=frame.copy()
                #masking
                MaskCoord=np.array(((3,714),(224,303),(1027,311),(1264,715),(1269,12),(13,18)))
                #310,473,294,686,882,706,889,419
                #3,714,224,303,1027,311,1264,715,1269,12,13,18

                cv2.fillPoly(masking_frame, pts=[MaskCoord], color=(255, 255, 255))
                cv2.imshow('CAM LIVE', frame)
                #print(results)
                #cv2.imshow('CAM LIVE MASK', masking_frame)
                if len(results[0].boxes.cls) > 0 :
                    try:
                        ntp_count=len(results[0].boxes)
                        
                    except:
                        pass
                    try:
                        bus_count=len(results[1].boxes)
                        print("bus count: "+str(bus_count))
                    except:
                        pass
                    print("################")
                    print(str(results[0].boxes.cls))
                    print("ntp count: "+str(ntp_count))
                    print(results[0].boxes.id)
                    print("################")
                    # print(results[0].id.tolist())
                    #print(results[0].)
                    for i in results[0].boxes :
                        # xyxy = i.xyxy
                        # print("################")
                        # print(i.data.tolist()[0][4])
                        # print("################")

                        id_box=i.data.tolist()[0][4]
                        class_id = results[0].names[i.cls[0].item()]
                        cords = i.xyxy[0].tolist()
                        cords = [round(x) for x in cords]
                        conf = round(i.conf[0].item(), 2)
                        try:
                            print("---")
                            #print(str(i.id.tolist())[1][0])
                            #print(str(i.id.tolist()))
                            print("data: "+str(i.data.tolist()))
                            print("Object type:", class_id)
                            print("Coordinates:", cords)
                            print("Probability:", conf)
                            print("temp_id: "+str(temp_id)+" class_id: "+str(id_box))
                            print("---")
                        except:
                            pass

                        if id_box!= temp_id and flag==1: 
                            sound_thread.start()
                            start_time = time.time()
                            flag=0
                            state_recording=0
                            date_time = datetime.now().strftime("_%d%m%Y_%H:%M:%S")
                            file_name=date_time+"_"+str(int(id_box))
                            
                            print("PICT SAVED")

                        if int(time.time() - start_time) == 10:
                            flag=1
                            output.release()
                            vid_writer.release()
                            get_fps = True
                        
                            print("FLAG SUDAH MENJADI 1 KEMBALI")

                        if int(time.time() - start_time) > 10:
                            flag=1
                            output.release()
                            vid_writer.release()
                            get_fps = True
                            print("FLAG SUDAH MENJADI 1 KEMBALI")

                        print("*****")

                        try:
                            print(str(int(time.time() - start_time)))
                            print("FLAG "+flag)
                            print("STATE_RECORDING "+state_recording)
                        except:
                            pass
                        print("*****")
                    temp_id=id_box

                #RECORDING
                try:        
                    if flag==0 and int(time.time() - start_time) < 11:
                        if get_fps :
                            print("ADA DETEKSI")
                            get_fps = False
                            fps = cap.get(cv2.CAP_PROP_FPS)
                            h, w, c = frame.shape
                            cv2.imwrite("./image/IMG"+file_name+".jpg", frame)
                            output = cv2.VideoWriter("./video/VID"+file_name+"-mpeg.avi", cv2.VideoWriter_fourcc(*'MPEG'), fps, (w, h))
                            vid_writer = cv2.VideoWriter("./video/VID"+file_name+"-mjpg.avi", cv2.VideoWriter_fourcc(*'MJPG'), fps, (w, h))
                        
                        output.write(frame)
                        vid_writer.write(frame)
                        print("RECORDING FRAME")
                        #return {"status":"mode_auto_aktif","cctv":"aktif","recording":"aktif"}
                except:
                    print("TIDAK ADA DETEKSI")
                    #return {"status":"mode_auto_aktif","cctv":"aktif","recording":"tidak_aktif"}
                    pass
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            else:
                break

        cap.release()
        cv2.destroyAllWindows()
        
# from fastapi import Depends, FastAPI, HTTPException, status, Form
# from fastapi.security import HTTPBasic, HTTPBasicCredentials
# import uvicorn
# from starlette.middleware import Middleware
# from starlette.middleware.cors import CORSMiddleware

# app = FastAPI()
# security = HTTPBasic()

# origins = ["*"]
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
#     expose_headers=["*"])

# if __name__ == '__main__':
#     uvicorn.run("main:app", host="localhost", port=8100,log_level="info",reload=True)