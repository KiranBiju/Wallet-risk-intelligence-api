import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, classification_report

#LOAD DATA

df = pd.read_csv("db/wallet_dataset.csv")

df["high_risk_ratio"] = df["high_risk_interactions"] / df["tx_frequency"]
df["high_risk_ratio"] = df["high_risk_ratio"].fillna(0)


FEATURES = [
    "tx_frequency",
    "avg_tx_value",
    "unique_interactions",
    "contract_calls",
    "high_risk_interactions",
    "high_risk_ratio"   
]

X = df[FEATURES]
y = df["label"]

#TRAIN TEST SPLIT

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

#SCALING

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

#MODEL

model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced"
)

#TRAIN

model.fit(X_train_scaled, y_train)

#EVALUATE

y_pred = model.predict(X_test_scaled)

print("\nMODEL METRICS")
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Precision:", precision_score(y_test, y_pred))
print("Recall:", recall_score(y_test, y_pred))

print("\nCLASSIFICATION REPORT")
print(classification_report(y_test, y_pred))


print("\nFEATURE IMPORTANCE")
importance = dict(zip(FEATURES, model.coef_[0]))
for k, v in importance.items():
    print(f"{k}: {round(v, 4)}")


joblib.dump(model, "ml/risk_model_v2.pkl")
joblib.dump(scaler, "ml/scaler_v2.pkl")

print("\nModel + Scaler saved (v2)")