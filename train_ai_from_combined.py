import json
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib

# Загружаем объединённый датасет
filename = "tetris_dataset_combined.json"
print(f"📂 Загружается датасет: {filename}")

with open(filename) as f:
    data = json.load(f)

X = []
y = []

for step in data:
    board_flat = np.array(step["board"]).flatten()
    piece_type = step["piece"]["type"]
    piece_type_encoded = ord(piece_type) / 90  # от 0.7 до 1.0
    input_vector = np.append(board_flat, piece_type_encoded)
    
    X.append(input_vector)
    y.append(step["move"])

X = np.array(X)
y = np.array(y)

# Преобразуем действия в числа
encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)

# Разделим на тренировочную и тестовую выборку
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Обучаем RandomForest
model = RandomForestClassifier(n_estimators=100, n_jobs=-1)
model.fit(X_train, y_train)

# Оцениваем
accuracy = model.score(X_test, y_test)
print(f"🎯 Точность на тесте: {accuracy:.4f}")

# Сохраняем модель и действия
joblib.dump(model, "tetris_rf_model.pkl")
with open("action_encoder.json", "w") as f:
    json.dump(encoder.classes_.tolist(), f)

print("✅ Модель сохранена как tetris_rf_model.pkl")