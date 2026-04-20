import numpy as np
from scipy.interpolate import CubicSpline
import pandas as pd
import requests
import time
from io import StringIO
from consts import *
import create_model
from ingestion import *

output_mapping, model = create_model.create_model("../datasets")

pad_len = max(len(o) + 2 for o in output_mapping)

CALIBRATION_STEPS = 4

def webserver():
    sittimer = 0
    state_window = []
    prevstate = "standing"
    prevwindow = "standing"
    last_sit_to_stand = 0
    last_delta = 1
    step = 0
    
    standingsum = 0
    sittingsum = 0
    sitting = 0
    rightlegup = 0 #sock 1 up
    leftlegup = 0 #sock 2 up
    
    s = requests.session()
    data = pd.DataFrame()
    calibration_step = 0
    while True:
        try:
            new_data = pd.read_json(
                StringIO('{"0": ' + s.get("http://sock_boss.local").text + "}"),
                orient="index",
            )[input_cols]
            linearize(new_data)
            data: pd.DataFrame = pd.concat([data, new_data])
            data = data.tail(WINDOW_SIZE)
            
            sum1 = 2*new_data[["heel1","ball11","ball12"]].sum(axis=1)[0]
            sum2 = new_data[["heel2","ball21","ball22"]].sum(axis=1)[0]
            
            summer = sum1+sum2
            delta = sum1-sum2
            
            if calibration_step == CALIBRATION_STEPS:
                ml_result = model([ml_inputs(data)])
                
                #print(sum1)
                #print(sum2)
                #print(delta)
                output = model([ml_inputs(data)])
                print("\n".join(f"{k:<{pad_len}}{v:.10f}" for k, v in output.items()), end="\n\n")
                sorted_output = {k: v for k, v in sorted(output.items(), key=lambda item: item[1])}
                keys = list(sorted_output.keys())
                cross_legged = False
                
                
                
                state_window.append(keys[-1])
                if len(state_window)>5: state_window.pop(0)
                most_occuring = max(set(state_window), key=state_window.count)
                               
                
                
                state_fin = most_occuring
                if sorted_output[keys[-1]] < 0.5:
                    state_fin = "unknown"
                    
                if state_fin == "sitting":
                    if summer>standingsum-abs(standingsum-sittingsum)/2:
                        state_fin = "standing"
                        
                elif state_fin == "standing":
                    if summer<standingsum-abs(standingsum-sittingsum)/2:
                        state_fin = "sitting"
                
                
                
                if state_fin == "sitting":
                    if sorted_output[keys[-1]]>0.65:
                        sittimer = time.time()
                    if delta<rightlegup+(abs(rightlegup-sitting))*0.6:
                        cross_legged = True
                    if delta>leftlegup-(abs(leftlegup-sitting))*0.4:
                        cross_legged = True
                
                if state_fin == "standing":
                    if sorted_output[keys[-1]]>0.6:
                        if prevwindow == "sitting":
                            last_sit_to_stand = time.time()-sittimer
                
                
                
                
                if keys[-1] == "walking" or keys[-1] == "stairs":
                    if delta<0 and last_delta>=0:
                        step+=1
                    if delta>0 and last_delta<=0:
                        step+=1
                
                #maybe if sitting confidence is below like 0.6 or 0.5 then
                
                print(keys[-1],sorted_output[keys[-1]])
                print("Cross-legged:",cross_legged, int(delta))
                print("Prev-sitstand",last_sit_to_stand)
                print("Windowed-stat", most_occuring)
                print("Decided-state",state_fin)
                print("Steps",step)
                print()
                
                last_delta = delta
                prevwindow = most_occuring
                prevstate = keys[-1]
                        #if sitting and starting to stand then walking spikes over 0.1 for a bit, detect that for actual standing detection
                        
                        #calibration wise - calibrate standing weight, calibrate sitting weight
            elif calibration_step == 0:
                print("Please stand for 3 seconds and then press CTRL+C to calibrate.")
            elif calibration_step == 1:
                print("Please sit for 3 seconds and then press CTRL+C to calibrate.")
            elif calibration_step == 2:
                print("Please sit crossleg with right leg up for 3 seconds and then press CTRL+C to calibrate.")
            elif calibration_step == 3:
                print("Please sit crossleg with left leg up for 3 seconds and then press CTRL+C to calibrate.")
            if calibration_step < CALIBRATION_STEPS:
                print("Delta: ",delta)
                print("Sum: ",summer)
            time.sleep(1 / SAMPLE_RATE)
        except KeyboardInterrupt as e:
            if calibration_step >= CALIBRATION_STEPS:
                print("Standingsum:",standingsum)
                print("Sittingsum:",sittingsum)
                print("Sitting:",sitting)
                print("Right-up:",rightlegup)
                print("Left-up:",leftlegup)
                if input("Press q and enter to exit. Otherwise, recalibrating.") == "q":
                    raise e
                calibration_step = 0
            elif calibration_step == 0:
                standingsum = summer
                calibration_step+=1
            elif calibration_step == 1:
                sittingsum = summer
                sitting = delta
                calibration_step+=1
            elif calibration_step == 2:
                rightlegup = delta
                calibration_step+=1
            elif calibration_step == 3:
                leftlegup = delta
                calibration_step+=1
        except requests.exceptions.ConnectionError:
            print("Connection failed. Trying again.")
webserver()
