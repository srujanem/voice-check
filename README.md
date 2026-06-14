# VoiceCheck: The Enterprise AI Detection Suite

VoiceCheck is a comprehensive, full-stack machine learning platform designed to detect AI-generated content across all major media formats: **Audio, Images, Text, and Video**. 

Built with a lightweight HTML/Vanilla JS frontend and a powerful Python/TensorFlow backend, the suite offers enterprise-grade features including Explainable AI, PDF reporting, and usage analytics.

## 🌟 Core Features & Architecture

### 1. The Core AI Engine (Backend)
The brain of the operation lives in `app.py`, a Flask web server that handles API requests from the frontend.
* **Image & Video AI**: Uses a custom-trained Convolutional Neural Network (CNN) built with TensorFlow/Keras (`model.h5` and `scaler.pkl`).
* **Text AI**: Uses a TF-IDF Vectorizer combined with a Logistic Regression model trained locally (`train_text.py`) to classify linguistic patterns typical of Large Language Models.
* **Audio AI**: Designed to convert audio waveforms into Mel-Spectrograms (images of sound) and run them through the vision model to detect synthetic voice artifacts.

### 2. The Four Pillars of Detection
The platform features four dedicated tools:
* **🎙️ Voice Detection (`voice-ui/`)**: Upload or record audio. The system analyzes the vocal frequencies for robotic or synthetic signatures.
* **🖼️ Image Detection (`deepfake-ui/`)**: Drag and drop images. The CNN analyzes pixel-level anomalies and artifacts left behind by generative models like Midjourney or Stable Diffusion.
* **📝 Text Detection (`text-ui/`)**: Paste an essay or article. The tool features **Explainable AI (XAI)**—it doesn't just give a score, it highlights the exact sentences in red that it suspects were written by an AI (like ChatGPT), leaving human sentences green.
* **🎥 Video Detection (`video-ui/`)**: Upload an MP4. The Python backend uses `ffmpeg` to extract frames evenly across the video's timeline, running each frame through the AI to calculate an aggregate deepfake probability score.

### 3. Professional Utilities
To elevate the suite into a true SaaS product, several global utilities were integrated:
* **📊 Analytics Dashboard (`dashboard-ui/`)**: A dedicated command center utilizing `Chart.js` to visualize your detection history. It tracks total scans, your AI-vs-Human discovery ratio, and plots a timeline of your activity.
* **🗂️ Global History Drawer (`history.js`)**: A sliding sidebar accessible from any page. It uses browser `localStorage` to keep a persistent log of your last 50 scans, complete with color-coded success/danger tags.
* **📄 PDF Generation**: Every tool includes a "Download PDF Report" button. Using `html2pdf.js`, the platform instantly takes a snapshot of your scan results, confidence rings, and metrics, formatting them into a professional, printable A4 document.

### 4. Advanced Frontend Design
The User Interface was built from scratch without bulky CSS frameworks.
* **Dynamic Glassmorphism**: Features an advanced CSS/JS physics engine where the main navigation cards tilt in 3D space, tracking the user's mouse and casting realistic light glares.
* **Theme Engine (`theme.js`)**: A robust Light/Dark mode toggle that seamlessly updates CSS variables (`global.css`) across all pages instantly.
* **Fluid Animations**: Custom keyframe animations for scanning lasers, counting-up numbers, and SVG confidence rings that dynamically fill up based on the AI's percentage score.

## 🚀 Running the Project

1. **Install Dependencies**:
   ```bash
   pip install flask flask-cors tensorflow pillow scikit-learn imageio[ffmpeg]
   ```
2. **Train the Text Model**:
   ```bash
   python train_text.py
   ```
3. **Start the Backend**:
   ```bash
   python app.py
   ```
4. **Launch the Frontend**:
   Open `index.html` in your browser!
