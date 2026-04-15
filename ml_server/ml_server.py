import numpy as np
import pandas as pd
import requests
import time
from io import StringIO

SAMPLE_RATE = 5
WINDOW_SIZE = 10 * SAMPLE_RATE


def max_fft(s: np.ndarray):
    freqs = np.fft.rfftfreq(len(s), 1 / SAMPLE_RATE)
    ffts = np.abs(np.fft.rfft(s - s.mean()))
    i = ffts.argmax()
    return (freqs[i], ffts[i])


def runml(df: pd.DataFrame):
    max_ffts = {}
    for col in df.columns:
        res = max_fft(df[col].values)
        max_ffts[col + "freq"] = "%.2f" % res[0]
        max_ffts[col + "mag"] = "%.2f" % res[0]
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
        print(runml(data))
        time.sleep(1 / SAMPLE_RATE)


webserver()
