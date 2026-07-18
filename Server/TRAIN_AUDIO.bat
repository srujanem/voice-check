@echo off
echo.
echo ============================================
echo   TRAIN VOICESHIELD (Audio Detector)
echo ============================================
echo.
echo   GPU: NVIDIA RTX 4050 (6GB VRAM)
echo   Mixed Precision: ON (fp16)
echo   Batch Size: 8
echo.
echo   Required data structure:
echo     %~dp0data\audio\human\  (real voice files)
echo     %~dp0data\audio\ai\     (AI voice files)
echo.
echo   Supported formats: .wav .mp3 .ogg .flac .m4a
echo.
cd /d "%~dp0"
python -m ml.audio.train
echo.
echo Training complete! Model saved to trained_models/
pause
