from io import StringIO
import time
import requests
import pandas as pd
from consts import *
import sys

def read_raw(target: str, delay: int):
    for i in range(delay,0,-1):
        print(i)
        time.sleep(1)
    s = requests.session()
    data = pd.DataFrame()
    try:
        while True:
            new_data = pd.read_json(
                StringIO('{"0": ' + s.get("http://sock_boss.local").text + "}"),
                orient="index",
            )
            data = pd.concat([data, new_data], ignore_index=True)
            print(new_data)
            time.sleep(1 / SAMPLE_RATE)
    except:
        data.to_csv(target)
        
read_raw(sys.argv[1],2)