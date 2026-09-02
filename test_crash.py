import sys
import traceback
sys.path.append(r"D:\Server\ai-training-panel\python_engine")
import inference

print("Testing image inference...")
try:
    res = inference.run_image_inference(r"D:\Server\ai-training-panel\node_server\uploads\738e3a06ef40cf3aa4908be8d254b77d")
    print(res)
except Exception as e:
    traceback.print_exc()
