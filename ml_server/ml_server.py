import numpy as np
import pandas as pd
import requests
import time
from io import StringIO
from math import floor

SAMPLE_RATE = 10
WINDOW_SIZE = floor(2.5 * SAMPLE_RATE)


def max_fft(s: np.ndarray):
    mean = s.mean()
    freqs = np.fft.rfftfreq(len(s), 1 / SAMPLE_RATE)
    ffts = np.abs(np.fft.rfft(s - mean))
    i = ffts.argmax()
    return (freqs[i], ffts[i], mean)


def runml(df: pd.DataFrame):
    max_ffts = {}
    for col in df.columns:
        if col == "time":
            continue
        res = max_fft(df[col].values)
        max_ffts[col + "freq"] = "%.2f" % res[0]
        max_ffts[col + "mag"] = "%.2f" % res[1]
        max_ffts[col + "mean"] = "%.2f" % res[2]
    return max_ffts


def simulate(df: pd.DataFrame):
    runml(df.rolling(window=WINDOW_SIZE))


def webserver():
    s = requests.session()
    data = pd.DataFrame()
    while True:
        data: pd.DataFrame = pd.concat(
            [
                data,
                pd.read_json(
                    StringIO('{"0": ' + s.get("http://sock_boss.local").text + "}"),
                    orient="index",
                ),
            ]
        )
        data = data.tail(WINDOW_SIZE)
        ml = runml(data)
        print("")
        for k, v in ml.items():
            print(k, v)
        time.sleep(1 / SAMPLE_RATE)


webserver()
