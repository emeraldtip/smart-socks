from io import StringIO
import time
import requests
import pandas as pd
from consts import *


def read_raw(target: str):
    s = requests.session()
    data = pd.DataFrame()
    try:
        while True:
            new_data = pd.read_json(
                StringIO('{"0": ' + s.get("http://sock_boss.local").text + "}"),
                orient="index",
            )
            data = pd.concat([data, new_data])
            time.sleep(1 / SAMPLE_RATE)
    except:
        data.to_csv(target)