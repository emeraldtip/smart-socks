import ingestion
import sklearn
from consts import *
import pandas as pd
import os
import itertools
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor

def process_subject(subject_idx, activity_idx, df, sum1, sum2):
    inputs = []
    outputs = []
    subjects = []
    df[["heel1", "ball11", "ball12"]] /= sum1
    df[["heel2", "ball21", "ball22"]] /= sum2
    for i in range(df.shape[0] + 1 - WINDOW_SIZE):
        inputs.append(ingestion.ml_inputs(df.iloc[i : i + WINDOW_SIZE]))
        outputs.append(activity_idx)
        subjects.append(subject_idx)
    return inputs, outputs, subjects

def _uninit_model():
    return sklearn.calibration.CalibratedClassifierCV(sklearn.ensemble.RandomForestClassifier(class_weight="balanced", random_state=42, n_jobs=-1))

def create_model(dataset_path: str, test=False):
    inputs = []
    outputs = []
    subjects = []
    output_mapping = {}
    n_activities = 0
    subject_set = os.listdir(dataset_path)
    executor = ProcessPoolExecutor()
    futures = []
    for subject_idx, subject in enumerate(subject_set):
        subject_path = os.path.join(dataset_path, subject)
        sum1 = 0.0
        sum2 = 0.0
        n_sums = 0
        raw_subject_inputs = {}
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
                sum1 += df[["heel1", "ball11", "ball12"]].sum(axis=0).sum()
                sum2 += df[["heel2", "ball21", "ball22"]].sum(axis=0).sum()
                n_sums += len(df.columns)
        if n_sums == 0:
            sum1 = 1.0
            sum2 = 1.0
        else:
            sum1 /= n_sums
            sum2 /= n_sums
        for activity_idx, dfs in raw_subject_inputs.items():
            for df in dfs:
                futures.append(executor.submit(process_subject, subject_idx, activity_idx, df, sum1, sum2))
    for future in futures:
        input_part, output_part, subject_part = future.result()
        inputs += input_part
        outputs += output_part
        subjects += subject_part
    if not test:
        clf = _uninit_model()
        clf.fit(inputs, outputs)
        return list(output_mapping.keys()), (lambda windows: dict(zip(output_mapping, *clf.predict_proba(windows).tolist())))
    logo = sklearn.model_selection.LeaveOneGroupOut();
    labels = list(output_mapping.keys())
    outputs_true = []
    outputs_test = []
    for i, (train_idxs, test_idxs) in enumerate(logo.split(inputs, outputs, subjects)):
        print(f"Fold {i}")
        clf = _uninit_model()
        clf.fit([inputs[i] for i in train_idxs], [outputs[i] for i in train_idxs])
        outputs_test += list(clf.predict([inputs[i] for i in test_idxs]))
        outputs_true += [outputs[i] for i in test_idxs]
    # outputs_test = list(itertools.chain.from_iterable(future.result() for future in futures))
    labels = list(output_mapping.keys())
    cmat = sklearn.metrics.confusion_matrix(outputs_true, outputs_test, labels=list(output_mapping.values()), normalize="pred")
    disp = sklearn.metrics.ConfusionMatrixDisplay(cmat, display_labels=labels)
    disp.plot()
    plt.show()

if __name__=="__main__":
    create_model("../datasets", True)