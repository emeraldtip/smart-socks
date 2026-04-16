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
    s = requests.session()
    data = pd.DataFrame()
    while True:
        new_data = pd.read_json(
            StringIO('{"0": ' + s.get("http://sock_boss.local").text + "}"),
            orient="index",
        )[input_cols]
        linearize(new_data)
        data: pd.DataFrame = pd.concat([data, new_data])
        data = data.tail(WINDOW_SIZE)
        #ml = runml(data)
        #print("")
        # for k, v in ml.items():
            # print(k, v)
        #for k, v in new_data.to_dict('records')[0].items():
        #    print(k,v)
        ml_result = model([ml_inputs(data)])
        print("\n".join(f"{k:<{pad_len}}{v}" for k, v in model([ml_inputs(data)]).items()), end="\n\n")
        time.sleep(1 / SAMPLE_RATE)


webserver()
