from sklearn.ensemble import IsolationForest
import numpy as np

def detectar_anomalias(montos):
    model = IsolationForest(contamination=0.05)  # 5% de anomalías
    X = np.array(montos).reshape(-1, 1)
    preds = model.fit_predict(X)
    return preds  # -1 = anomalía, 1 = normal