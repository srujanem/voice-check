import os
import re

inference_path = r'D:\Server\ai-training-panel\python_engine\inference.py'

with open(inference_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Revert Image Inference to use the custom keras model
image_new = '''def run_image_inference(file_path):
    try:
        import tensorflow as tf
        from PIL import Image
        import numpy as np
        
        # Load the custom-trained model optimized for the user's dataset
        model_path = os.path.join(os.path.dirname(__file__), "../../voice-check/voice-check/model_image_best_grid.keras")
        if not os.path.exists(model_path):
            return {"error": "Image model not found."}
            
        # We load it every time or globally? For now, we load it here to be safe and avoid global state conflicts.
        # But actually, let's cache it globally for speed.
        global custom_image_model
        if 'custom_image_model' not in globals() or custom_image_model is None:
            print("[INFO] Loading custom model_image_best_grid.keras...")
            custom_image_model = tf.keras.models.load_model(model_path)
            
        img_size = (150, 150)
        # Try finding the expected input shape dynamically
        try:
            input_shape = custom_image_model.input_shape
            if input_shape and len(input_shape) >= 3:
                img_size = (input_shape[1], input_shape[2])
        except:
            pass

        img = Image.open(file_path).convert('RGB')
        img = img.resize(img_size)
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        pred = custom_image_model.predict(img_array)[0][0]
        
        # Our custom model outputs a sigmoid probability where 1 = AI, 0 = Human
        is_ai = bool(pred > 0.5)
        confidence = float(pred * 100) if is_ai else float((1.0 - pred) * 100)

        return {
            "is_ai": is_ai,
            "confidence": round(confidence, 1),
            "model": "Keras Custom CNN (Trained on Family Dataset)",
            "details": f"Raw sigmoid output: {pred:.4f}"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
'''

content = re.sub(r'def run_image_inference\(file_path\):.*?return \{.*?\}', image_new, content, flags=re.DOTALL)

with open(inference_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully reverted image inference to the custom model_image_best_grid.keras!")
