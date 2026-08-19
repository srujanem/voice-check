python "D:\voice-check\voice-check\download_ai_images.py"
echo "Downloads finished. Starting augmentation..."
python "D:\voice-check\voice-check\augment_ai_images.py"
echo "Augmentation finished. Starting training..."
python "D:\voice-check\voice-check\train_image_fixed.py"
echo "Training finished. Restarting backend..."
taskkill /F /IM python.exe /T
Start-Sleep 2
Start-Process -FilePath "python" -ArgumentList "run.py" -WorkingDirectory "D:\voice-check\voice-check" -WindowStyle Hidden
echo "Backend restarted successfully!"
