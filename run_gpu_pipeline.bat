@echo off
echo Running Voice AI Training on GPU...
python train_voice_gpu.py
echo.
echo Running Text AI Fine-Tuning on GPU...
python train_text_gpu.py
echo.
echo ALL GPU TASKS COMPLETED!
