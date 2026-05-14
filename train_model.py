
import os
import numpy as np
import static_ffmpeg
static_ffmpeg.add_paths()
import librosa
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def extract_features(path):
    try:
        y, sr = librosa.load(path, duration=5, sr=22050)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        mel = librosa.feature.melspectrogram(y=y, sr=sr)
        return np.hstack([
            np.mean(mfcc.T, axis=0),
            np.mean(chroma.T, axis=0),
            np.mean(mel.T, axis=0)
        ])
    except Exception as e:
        print(f"Error: {e}")
        return None

X, y = [], []

print("Loading human voices...")
for f in os.listdir("dataset/human"):
    if f.lower().endswith(('.wav', '.mp3', '.webm', '.m4a', '.flac')):
        feat = extract_features(f"dataset/human/{f}")
        if feat is not None:
            X.append(feat)
            y.append(0)

print("Loading AI voices...")
for f in os.listdir("dataset/ai"):
    if f.lower().endswith(('.wav', '.mp3', '.webm', '.m4a', '.flac')):
        feat = extract_features(f"dataset/ai/{f}")
        if feat is not None:
            X.append(feat)
            y.append(1)

print(f"Total samples: {len(X)}")

if len(X) < 4:
    print("Add more audio files (.wav, .mp3, .flac) to dataset/human and dataset/ai!")
    exit()

X_train, X_test, y_train, y_test = train_test_split(
    np.array(X), np.array(y), test_size=0.2, random_state=42
)

model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

print(f"Accuracy: {accuracy_score(y_test, model.predict(X_test))*100:.1f}%")
joblib.dump(model, "model.pkl")
print("model.pkl saved!")