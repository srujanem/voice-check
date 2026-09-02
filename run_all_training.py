import os
import subprocess
import time

print("Waiting for ViT GPU training to finish...")
# Since ViT is already running, we can just monitor python processes.
# But actually, it's safer to just run train_image_advanced.py AFTER the current PID finishes.
# I'll find the python PID that is running train_vit_gpu.py
import psutil

vit_pid = None
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        if proc.info['name'] == 'python.exe' and proc.info['cmdline']:
            if 'train_vit_gpu.py' in proc.info['cmdline'][1]:
                vit_pid = proc.info['pid']
                break
    except:
        pass

if vit_pid:
    print(f"Found ViT training running at PID {vit_pid}. Waiting for it to finish...")
    proc = psutil.Process(vit_pid)
    proc.wait()
    print("ViT finished!")
else:
    print("ViT not found. Maybe it already finished or crashed.")

print("Starting TensorFlow training...")
subprocess.run(["python", "train_image_advanced.py"])
print("ALL TRAINING COMPLETE!")
