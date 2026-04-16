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



def webserver():
    sittimer = 0
    state_window = []
    prevstate = "standing"
    prevwindow = "standing"
    last_sit_to_stand = 0
    last_delta = 1
    step = 0
    
    s = requests.session()
    data = pd.DataFrame()
    # calibrated = False
    # calibration = None
    # print("Press CTRL+C to calibrate")
    while True:
        # try:
        new_data = pd.read_json(
            StringIO('{"0": ' + s.get("http://sock_boss.local").text + "}"),
            orient="index",
        )[input_cols]
        linearize(new_data)
        # if calibrated:
            # new_data /= calibration
        data: pd.DataFrame = pd.concat([data, new_data])
        data = data.tail(WINDOW_SIZE)
        #ml = runml(data)
        #print("")
        # for k, v in ml.items():
            # print(k, v)
        #for k, v in new_data.to_dict('records')[0].items():
        #    print(k,v)
        # if calibrated:
        ml_result = model([ml_inputs(data)])
        sum1 = new_data[["heel1","ball11","ball12"]].sum(axis=1)[0]
        sum2 = new_data[["heel2","ball21","ball22"]].sum(axis=1)[0]
        #print(sum1)
        #print(sum2)
        summer = sum1+sum2
        delta = sum1-sum2
        #print(delta)
        output = model([ml_inputs(data)])
        print("\n".join(f"{k:<{pad_len}}{v:.10f}" for k, v in output.items()), end="\n\n")
        sorted_output = {k: v for k, v in sorted(output.items(), key=lambda item: item[1])}
        keys = list(sorted_output.keys())
        cross_legged = False
        
        state_window.append(keys[-1])
        if len(state_window)>5: state_window.pop(0)
        most_occuring = max(set(state_window), key=state_window.count)
        
        if keys[-1] == "sitting_normal":
            if sorted_output[keys[-1]]>0.65:
                sittimer = time.time()
            if delta<-55:
                cross_legged = True
            if delta>5:
                cross_legged = True
        
        if most_occuring == "standing":
            if sorted_output[keys[-1]]>0.6:
                if prevwindow == "sitting_normal":
                    last_sit_to_stand = time.time()-sittimer
        
        if keys[-1] == "walking" or keys[-1] == "stairs":
            if delta<0 and last_delta>=0:
                step+=1
            if delta>0 and last_delta<=0:
                step+=1
        
        #maybe if sitting confidence is below like 0.6 or 0.5 then
        
        print(keys[-1],sorted_output[keys[-1]])
        print("Cross-legged:",cross_legged)
        print("Prev-sitstand",last_sit_to_stand)
        print("Windowed-stat", most_occuring)
        print("Steps",step)
        print()
        
        last_delta = delta
        prevwindow = most_occuring
        prevstate = keys[-1]
                #if sitting and starting to stand then walking spikes over 0.1 for a bit, detect that for actual standing detection
                
                #calibration wise - calibrate standing weight, calibrate sitting weight
        time.sleep(1 / SAMPLE_RATE)
        # except KeyboardInterrupt as e:
        #     if calibrated:
        #         raise e
        #     print("Calibrated")
        #     calibrated = True
        #     calibration = data.max(axis=0)
        #     data /= calibration

webserver()
