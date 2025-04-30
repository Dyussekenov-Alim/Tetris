import json
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib

# Найдём последний датасет
dataset_files = [f for f in os.listdir() if f.startswith("tetris_dataset") and f.endswith(".json")]
dataset_files.sort()
filename = dataset_files[-1]

print(f"Загружается датасет: {filename}")
with open(filename) as f:
    data = json.load(f)

X = []
y = []

for step in data:
    board_flat = np.array(step["board"]).flatten()
    piece_type = step["piece"]["type"]
    piece_type_encoded = ord(piece_type) / 90  # простая нормализация
    input_vector = np.append(board_flat, piece_type_encoded)
    X.append(input_vector)
    y.append(step["move"])

X = np.array(X)
y = np.array(y)

encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Используем RandomForest вместо нейросети
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Сохраняем модель и кодировщик
joblib.dump(model, "tetris_rf_model.pkl")
with open("action_encoder.json", "w") as f:
    json.dump(encoder.classes_.tolist(), f)

print("✅ Модель обучена и сохранена как tetris_rf_model.pkl")