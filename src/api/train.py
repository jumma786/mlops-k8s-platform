"""Train XGBoost model and save artifacts for K8s deployment."""

import os, json, numpy as np, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import roc_auc_score, f1_score
import xgboost as xgb

ARTIFACTS_DIR = "artifacts"

def train(data_path=None, random_state=42):
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    if data_path and os.path.exists(data_path):
        df = pd.read_csv(data_path, sep=";")
        df["y"] = (df["y"] == "yes").astype(int)
        source = data_path
    else:
        np.random.seed(random_state)
        n = 5000
        df = pd.DataFrame({
            "age": np.random.randint(18,95,n), "job": np.random.choice(["admin.","blue-collar","technician"],n),
            "marital": np.random.choice(["married","single"],n), "education": np.random.choice(["high.school","university.degree"],n),
            "default": np.random.choice(["no","unknown"],n), "housing": np.random.choice(["no","yes"],n),
            "loan": np.random.choice(["no","yes"],n), "contact": np.random.choice(["cellular","telephone"],n),
            "month": np.random.choice(["may","jun","jul"],n), "day_of_week": np.random.choice(["mon","tue","wed"],n),
            "campaign": np.random.randint(1,10,n), "pdays": np.where(np.random.rand(n)<0.13,np.random.randint(1,30,n),999),
            "previous": np.random.randint(0,5,n), "poutcome": np.random.choice(["nonexistent","failure"],n),
            "emp.var.rate": np.random.choice([-1.8,1.1],n), "cons.price.idx": np.random.uniform(92.2,94.8,n).round(3),
            "cons.conf.idx": np.random.uniform(-50.8,-26.9,n).round(1), "euribor3m": np.random.uniform(0.6,5.1,n).round(3),
            "nr.employed": np.random.choice([4963.6,5099.1],n), "y": (np.random.rand(n)<0.11).astype(int),
        })
        source = "synthetic"

    if "duration" in df.columns:
        df = df.drop(columns=["duration"])

    cat_cols = df.select_dtypes(include="object").columns.tolist()
    encoders = {}
    for col in cat_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = {v: int(i) for i, v in enumerate(le.classes_)}

    X = df.drop(columns=["y"]); y = df["y"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=random_state, stratify=y)

    model = xgb.XGBClassifier(n_estimators=200, max_depth=5, learning_rate=0.05,
        scale_pos_weight=8, eval_metric="logloss", verbosity=0, random_state=random_state)
    model.fit(X_train, y_train)

    auc = roc_auc_score(y_test, model.predict_proba(X_test)[:,1])
    f1  = f1_score(y_test, model.predict(X_test), zero_division=0)

    model.save_model(os.path.join(ARTIFACTS_DIR, "model.json"))
    json.dump(list(X.columns), open(os.path.join(ARTIFACTS_DIR, "feature_order.json"),"w"))
    json.dump(encoders, open(os.path.join(ARTIFACTS_DIR, "encoders.json"),"w"))
    json.dump({"model_type":"XGBoost","auc":round(auc,4),"f1":round(f1,4),
               "n_features":len(X.columns),"features":list(X.columns),
               "data_source":source}, open(os.path.join(ARTIFACTS_DIR,"model_info.json"),"w"), indent=2)

    print(f"Trained | AUC={auc:.4f} | F1={f1:.4f} | Source={source}")
    return auc

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--data-path", type=str, default=None)
    args = p.parse_args()
    train(data_path=args.data_path)
