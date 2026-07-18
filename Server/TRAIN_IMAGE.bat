@echo off
echo.
echo ============================================
echo   TRAIN PIXELGUARD (Image Detector)
echo ============================================
echo.
echo   GPU: NVIDIA RTX 4050 (6GB VRAM)
echo   Mixed Precision: ON (fp16)
echo   Batch Size: 12
echo   FFT Artifact Analysis: ON
echo.
echo   Required data structure:
echo     %~dp0data\images\human\  (real photos)
echo     %~dp0data\images\ai\     (AI generated images)
echo.
echo   Supported formats: .jpg .png .webp .bmp
echo.
cd /d "%~dp0"
python -m ml.image.train
echo.
echo Training complete! Model saved to trained_models/
pause
