from sklearn.ensemble import IsolationForest
import numpy as np
from typing import List

def detectar_anomalias(montos: List[float]) -> List[int]:
    
    try:
        if not montos:
            return []
            
        X = np.array(montos).reshape(-1, 1)
        
        # Configuración del modelo 
        model = IsolationForest(
            contamination=0.05,  # 5% de valores como anomalías
            random_state=42     
        )
        
        # Entrenamiento y predicción
        return model.fit_predict(X).tolist()
        
    except Exception as e:
        print(f"⚠️ Error en detección de anomalías: {str(e)}")
        return [1] * len(montos) 