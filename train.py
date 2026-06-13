import os
import numpy as np
import static_ffmpeg
static_ffmpeg.add_paths()
import librosa
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping

def extract_features(path):
    try:
        y, sr = librosa.load(path, duration=5, sr=22050)
        if len(y) == 0:
            return None
        if len(y) < 2048:
            y = np.pad(y, (0, 2048 - len(y)))
        noise_amp = 0.005 * np.random.uniform() * np.amax(y)
        y = y + noise_amp * np.random.normal(size=y.shape)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        pitch_values = pitches[magnitudes > np.median(magnitudes)]
        pitch_mean = np.mean(pitch_values) if len(pitch_values) > 0 else 0.0
        pitch_std  = np.std(pitch_values)  if len(pitch_values) > 0 else 0.0
        zcr = librosa.feature.zero_crossing_rate(y)
        rms = librosa.feature.rms(y=y)
        features = np.hstack([
            np.mean(mfcc.T, axis=0),
            np.std(mfcc.T, axis=0),
            np.mean(chroma.T, axis=0),
            np.std(chroma.T, axis=0),
            [pitch_mean, pitch_std],
            [np.mean(zcr), np.std(zcr)],
            [np.mean(rms), np.std(rms)],
        ])
        return features
    except Exception as e:
        print(f"  Error: {e}")
        return None

X, y = [], []
SUPPORTED = ('.wav', '.mp3', '.flac', '.webm', '.m4a', '.ogg')

print("Loading human voices...")
for f in os.listdir("dataset/human"):
    if f.lower().endswith(SUPPORTED):
        try:
            print(f"  {f}")
        except UnicodeEncodeError:
            print(f"  {f.encode('ascii', 'replace').decode('ascii')}")
        feat = extract_features(os.path.join("dataset/human", f))
        if feat is not None:
            X.append(feat)
            y.append(0)

print("Loading AI voices...")
for f in os.listdir("dataset/ai"):
    if f.lower().endswith(SUPPORTED):
        try:
            print(f"  {f}")
        except UnicodeEncodeError:
            print(f"  {f.encode('ascii', 'replace').decode('ascii')}")
        feat = extract_features(os.path.join("dataset/ai", f))
        if feat is not None:
            X.append(feat)
            y.append(1)

print(f"Total samples: {len(X)}")
if len(X) < 4:
    print("Add more audio files to dataset/human and dataset/ai!")
    exit()

X_arr = np.array(X)
y_arr = np.array(y)

X_train, X_test, y_train, y_test = train_test_split(
    X_arr, y_arr, test_size=0.2, random_state=42
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

# Build Deep Learning Model
model = Sequential([
    Dense(256, activation='relu', input_shape=(X_train_scaled.shape[1],)),
    BatchNormalization(),
    Dropout(0.4),
    Dense(128, activation='relu'),
    BatchNormalization(),
    Dropout(0.3),
    Dense(64, activation='relu'),
    BatchNormalization(),
    Dropout(0.2),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

early_stopping = EarlyStopping(
    monitor='val_loss',
    patience=10,
    restore_best_weights=True
)

print("Training deep learning model...")
model.fit(
    X_train_scaled, y_train,
    validation_data=(X_test_scaled, y_test),
    epochs=100,
    batch_size=32,
    callbacks=[early_stopping],
    verbose=1
)

y_pred_probs = model.predict(X_test_scaled)
y_pred = (y_pred_probs >= 0.5).astype(int).flatten()

print(f"Accuracy: {accuracy_score(y_test, y_pred)*100:.1f}%")
print(classification_report(y_test, y_pred, target_names=["Human", "AI"]))

model.save("model.keras")
joblib.dump(scaler, "scaler.pkl")
print("model.keras and scaler.pkl saved!")
print("Now run: python app.py")
