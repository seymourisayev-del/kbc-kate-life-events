"""Smoke test: TabPFN + XGBoost + SHAP on a toy dataset. Run: python scripts/hello_model.py

Also forces the TabPFN weights download, so do this once on good Wi-Fi.
"""
import sys
import time

import shap
from dotenv import load_dotenv
from sklearn.datasets import load_breast_cancer
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

load_dotenv()  # TABPFN_TOKEN

X, y = load_breast_cancer(return_X_y=True, as_frame=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
ok = True

try:
    t = time.time()
    xgb = XGBClassifier(n_estimators=200, max_depth=4).fit(X_train, y_train)
    auc = roc_auc_score(y_test, xgb.predict_proba(X_test)[:, 1])
    print(f"[OK]   XGBoost: AUC {auc:.3f} in {time.time() - t:.1f}s")

    shap_values = shap.TreeExplainer(xgb).shap_values(X_test)
    print(f"[OK]   SHAP: values shape {shap_values.shape}")
except Exception as e:
    ok = False
    print(f"[FAIL] XGBoost/SHAP: {type(e).__name__}: {e}")

try:
    from tabpfn import TabPFNClassifier

    t = time.time()
    clf = TabPFNClassifier().fit(X_train, y_train)
    auc = roc_auc_score(y_test, clf.predict_proba(X_test)[:, 1])
    print(f"[OK]   TabPFN: AUC {auc:.3f} in {time.time() - t:.1f}s")
except Exception as e:
    ok = False
    print(f"[FAIL] TabPFN: {type(e).__name__}: {e}")

sys.exit(0 if ok else 1)
