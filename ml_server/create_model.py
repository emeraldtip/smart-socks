import ingestion
import sklearn
from consts import *
import pandas as pd
import os
import itertools
import matplotlib.pyplot as plt

def uninit_model():
    return sklearn.calibration.CalibratedClassifierCV(sklearn.ensemble.RandomForestClassifier(class_weight="balanced"))

def create_model(dataset_path: str, test=False):
    inputs = []
    outputs = []
    subjects = []
    output_mapping = {}
    n_activities = 0
    subject_set = os.listdir(dataset_path);
    for subject_idx, subject in enumerate(subject_set):
        subject_path = os.path.join(dataset_path, subject)
        # calibration = pd.read_csv(os.path.join(subject_path, "calibration.csv"),index_col=0).squeeze()
        sum1 = 0.0
        sum2 = 0.0
        n_sums = 0
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
                df[["heel1", "ball11", "ball12"]] /= sum1
                df[["heel2", "ball21", "ball22"]] /= sum2
                for i in range(df.shape[0] + 1 - WINDOW_SIZE):
                    inputs.append(ingestion.ml_inputs(df.iloc[i : i + WINDOW_SIZE]))
                    outputs.append(activity_idx)
                    subjects.append(subject_idx)
    if not test:
        clf = uninit_model()
        clf.fit(inputs, outputs)
        return list(output_mapping.keys()), (lambda windows: dict(zip(output_mapping, *clf.predict_proba(windows).tolist())))
    logo = sklearn.model_selection.LeaveOneGroupOut();
    outputs_true = []
    outputs_test = []
    for i, (train_idxs, test_idxs) in enumerate(logo.split(inputs, outputs, subjects)):
        print(f"Fold {i}")
        clf = uninit_model()
        clf.fit([inputs[i] for i in train_idxs], [outputs[i] for i in train_idxs])
        outputs_test += list(clf.predict([inputs[i] for i in test_idxs]))
        outputs_true += [outputs[i] for i in test_idxs]
    labels = list(output_mapping.keys())
    cmat = sklearn.metrics.confusion_matrix(outputs_true, outputs_test, labels=list(output_mapping.values()), normalize="pred")
    disp = sklearn.metrics.ConfusionMatrixDisplay(cmat, display_labels=labels)
    disp.plot()
    plt.show()

if __name__=="__main__":
    create_model("../datasets", True)