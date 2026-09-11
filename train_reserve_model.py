import sqlite3
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# 1. Detect correct database file path automatically
if os.path.exists("database/mine_data.db"):
    db_path = "database/mine_data.db"
elif os.path.exists("mine_data.db"):
    db_path = "mine_data.db"
else:
    # If no database exists yet, create it inside the root directory
    db_path = "mine_data.db"

print(f"[i] Using database file at: {os.path.abspath(db_path)}")

# 2. Connect to DB and force table creation
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS reserves (
        borehole_id INTEGER PRIMARY KEY,
        latitude REAL,
        longitude REAL,
        depth_meters REAL,
        manganese_grade_percent REAL,
        target_label INTEGER
    )
''')

# 3. Populate data if table is empty
cursor.execute("SELECT COUNT(*) FROM reserves")
if cursor.fetchone()[0] == 0:
    print("[!] 'reserves' table empty. Inserting ground truth dataset...")
    sample_data = [
        (101, -27.2015, 22.9482, 45.2, 34.5, 1),
        (102, -27.2031, 22.9510, 60.0, 12.8, 0),
        (103, -27.1988, 22.9425, 38.0, 28.4, 1),
        (104, -27.2054, 22.9560, 75.5, 8.2, 0),
        (105, -27.1950, 22.9390, 52.1, 41.2, 1),
        (106, -27.2080, 22.9610, 80.0, 14.5, 0),
        (107, -27.2002, 22.9455, 41.8, 31.0, 1),
        (108, -27.1925, 22.9350, 30.5, 38.9, 1),
        (109, -27.2110, 22.9650, 95.0, 5.4, 0),
        (110, -27.2020, 22.9490, 49.0, 22.1, 1)
    ]
    cursor.executemany('''
        INSERT INTO reserves (borehole_id, latitude, longitude, depth_meters, manganese_grade_percent, target_label)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', sample_data)
    conn.commit()

# 4. Fetch data for ML Model
df_reserves = pd.read_sql_query("SELECT latitude, longitude, depth_meters, target_label FROM reserves", conn)
conn.close()

# 5. Model Training & Evaluation
X = df_reserves[['latitude', 'longitude', 'depth_meters']]
y = df_reserves['target_label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

preds = rf.predict(X_test)
acc = accuracy_score(y_test, preds)

print(f"[✓] Reserve Model Trained Successfully! Accuracy: {acc * 100:.2f}%")

import pickle
os.makedirs("models", exist_ok=True)
with open("models/reserve_model.pkl", "wb") as f:
    pickle.dump(rf, f)
print("[✓] Reserve Model Saved to 'models/reserve_model.pkl'")