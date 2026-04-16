import ingestion
import sklearn
from consts import *
import pandas as pd
import os
import itertools

def create_model(dataset_path: str):
    inputs = []
    outputs = []
    subjects = []
    output_mapping = {}
    n_activities = 0
    for subject_idx, subject in enumerate(os.listdir(dataset_path)):
        subject_path = os.path.join(dataset_path, subject)
        full_subject = pd.DataFrame()
        raw_subject_inputs = {}
        # subject_max = None
        for activity in os.listdir(subject_path):
            activity_path = os.path.join(subject_path, activity)
            if not os.path.isdir(activity_path):
                continue
            if activity not in output_mapping:
                output_mapping[activity] = n_activities
                n_activities += 1
            activity_idx = output_mapping[activity]
            raw_subject_inputs[activity_idx] = []
            for file in os.listdir(activity_path):
                print(activity, file)
                # ensures columns are in order and only selects wanted columns for ml_inputs
                df = pd.read_csv(os.path.join(activity_path, file))[ingestion.input_cols].dropna()
                ingestion.linearize(df)
                raw_subject_inputs[activity_idx].append(df)
                df_max = df.max(axis=0)
                # subject_max = df_max if subject_max is None else df_max.combine(subject_max, max)
        for activity_idx, dfs in raw_subject_inputs.items():
            for df in dfs:
                # df /= subject_max
                for i in range(df.shape[0] + 1 - WINDOW_SIZE):
                    inputs.append(ingestion.ml_inputs(df.iloc[i : i + WINDOW_SIZE]))
                    outputs.append(activity_idx)
                    subjects.append(subject_idx)
    # uncal_clf = sklearn.svm.LinearSVC();
    # uncal_clf = sklearn.gaussian_process.GaussianProcessClassifier()
    uncal_clf = sklearn.svm.SVC(class_weight="balanced")
    clf = sklearn.calibration.CalibratedClassifierCV(uncal_clf)
    clf.fit(inputs, outputs)
    return list(output_mapping.keys()), (lambda windows: dict(zip(output_mapping, *clf.predict_proba(windows).tolist())))