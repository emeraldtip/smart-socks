import numpy as np
from scipy.interpolate import CubicSpline
import pandas as pd
from consts import *

def r2a(other: float, resistances: np.ndarray) -> CubicSpline:
    resistances[:, 1] *= 4095 / (resistances[:, 1] + other)
    return CubicSpline(
        resistances[:, 1], resistances[:, 0], bc_type="natural", extrapolate=True
    )


# kg: resistance as measured from the hydraulic press
# units aren't too important; all fed into ML model, just want data to be linear-ish
linearization_data = {
    # sensor 5
    "heel1": r2a(
        1000,
        np.array(
            [
                [80.5 - 0.692, 380],
                [72.4 - 0.692, 580],
                [60.0 - 0.692, 710],
                [50.9 - 0.692, 900],
                [40.7 - 0.692, 1600],
                [31.5 - 0.692, 3400],
                [20.7 - 0.692, 9400],
                [11.5 - 0.692, 15200],
                [0.081, 31000],
                [0, 500000],
            ]
        ),
    ),
    # sensor 1
    "ball11": r2a(
        100,
        np.array(
            [
                [81.1 - 1.02, 92],
                [70.8 - 1.02, 104],
                [61.4 - 1.02, 123],
                [52.0 - 1.02, 141],
                [41.2 - 1.02, 171],
                [31.1 - 1.02, 210],
                [21.0 - 1.02, 280],
                [11.2 - 1.02, 366],
                [0.081, 16000],
                [0, 1000000],
            ]
        ),
    ),
    # sensor 2
    "ball12": r2a(
        100,
        np.array(
            [
                [81.0 - 1.02, 46],
                [70.8 - 1.02, 52],
                [61.2 - 1.02, 61],
                [50.9 - 1.02, 72],
                [41.5 - 1.02, 95],
                [31.5 - 1.02, 132],
                [21.1 - 1.02, 225],
                [11.2 - 1.02, 351],
                [0.081, 18000],
                [0, 500000],
            ]
        ),
    ),
    # sensor 4
    "heel2": r2a(
        10000,
        np.array(
            [
                [81.0 - 0.692, 1000],
                [71.0 - 0.692, 2000],
                [62.1 - 0.692, 3000],
                [50.6 - 0.692, 5000],
                [41.1 - 0.692, 12000],
                [33.3 - 0.692, 14000],
                [22.0 - 0.692, 38000],
                [12.4 - 0.692, 43000],
                [0.081, 150000],
                [0, 2000000],
            ]
        ),
    ),
    # sensor 6
    "ball21": r2a(
        2200,
        np.array(
            [
                [81.1 - 0.692, 430],
                [69.9 - 0.692, 750],
                [60.1 - 0.692, 1000],
                [50.8 - 0.692, 1900],
                [40.9 - 0.692, 3800],
                [31.4 - 0.692, 8300],
                [22.1 - 0.692, 8900],
                [9.9 - 0.692, 11800],
                [0.081, 26000],
                [0, 500000],
            ]
        ),
    ),
    # sensor 3
    "ball22": r2a(
        220, 
        np.array(
            [
                [82.0 - 1.02, 103],
                [72.2 - 1.02, 130],
                [62.3 - 1.02, 140],
                [51.9 - 1.02, 230],
                [41.2 - 1.02, 310],
                [31.1 - 1.02, 417],
                [21.9 - 1.02, 1810],
                [11.6 - 1.02, 15000],
                [0.081, 17000],
                [0, 500000],
            ]
        ),
    ),
}


def linearize(df: pd.DataFrame):
    for col in df.columns:
        if col not in linearization_data:
            continue
        df[col] = linearization_data[col](df[col])


def max_fft(s: np.ndarray):
    mean = s.mean()
    n_fft = len(s) * 4
    freqs = np.fft.rfftfreq(n_fft, 1 / SAMPLE_RATE)
    ffts = np.fft.rfft(s - mean, n_fft)
    abs_ffts = np.abs(ffts)
    i = abs_ffts.argmax()
    slope =  0
    if len(s)>1:
        slope,_ = np.polyfit(range(len(s)), s, 1)
    return (freqs[i], abs_ffts[i], np.angle(ffts[i])/(2*np.pi*freqs[i]) if i != 0 else 0, mean, slope)
    
    
fft_cols = ["heel1", "heel2", "ball11", "ball12", "ball21", "ball22"]
input_cols = fft_cols

def ml_inputs(df: pd.DataFrame):
    subset = df[input_cols]
    result = []
    for col in subset.columns:
        res = max_fft(subset[col].values)
        result.append(res[0]) # freq
        result.append(res[1]) # mag
        result.append(res[2]) # angle
        result.append(res[3]) # mean
        result.append(res[4]) # slope
    return result