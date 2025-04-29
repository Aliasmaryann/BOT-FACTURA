from sklearn.ensemble import IsolationForest
import numpy as np
from typing import List

'''def detectar_anomalias(montos):
    model = IsolationForest(contamination=0.05)  # 5% de anomalías
    X = np.array(montos).reshape(-1, 1)
    preds = model.fit_predict(X)
    return preds  # -1 = anomalía, 1 = normal'''


def detectar_anomalias(montos: List[float]) -> List[int]:
    """
    Detecta anomalías en una lista de montos usando Isolation Forest.
    
    Args:
        montos: Lista de montos a analizar (pueden ser subtotales o montos totales)
        
    Returns:
        Lista con predicciones: -1 para anomalía, 1 para normal
    """
    try:
        if not montos:
            return []
            
        # Convertimos a array numpy y redimensionamos
        X = np.array(montos).reshape(-1, 1)
        
        # Configuración del modelo (ajustable)
        model = IsolationForest(
            contamination=0.05,  # 5% de valores como anomalías (ajustable)
            random_state=42      # Para reproducibilidad
        )
        
        # Entrenamiento y predicción
        return model.fit_predict(X).tolist()
        
    except Exception as e:
        print(f"⚠️ Error en detección de anomalías: {str(e)}")
        return [1] * len(montos)  # Retorna todos como normales en caso de error