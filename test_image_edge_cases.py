import os
import cv2
import numpy as np
import tensorflow as tf

print("Loading Advanced Model...")
model = tf.keras.models.load_model('model_image_advanced.keras')

def evaluate_edge_case(image_path, modification="none"):
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return
        
    img = cv2.imread(image_path)
    if img is None: return
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    print(f"\n--- Testing Edge Case: {os.path.basename(image_path)} | Mod: {modification} ---")
    
    if modification == "heavy_jpeg":
        # Simulate heavy compression from social media
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 30]
        _, encimg = cv2.imencode('.jpg', img, encode_param)
        img = cv2.imdecode(encimg, 1)
    
    elif modification == "downscale":
        # Simulate someone screenshotting a thumbnail
        h, w = img.shape[:2]
        img = cv2.resize(img, (w//4, h//4))
    
    # Preprocess for model
    img_resized = cv2.resize(img, (224, 224))
    img_array = np.expand_dims(img_resized, axis=0).astype('float32')
    
    # Predict
    prob = model.predict(img_array, verbose=0)[0][0]
    
    is_human = prob > 0.5
    confidence = (prob if is_human else (1 - prob)) * 100
    label = "Human (Real)" if is_human else "AI-Generated"
    
    print(f"Prediction: {label}")
    print(f"Confidence: {confidence:.2f}%")

# Test an edge case if provided
test_img = "dataset_image/ai/sample.jpg" # Update with a real path to test
# evaluate_edge_case(test_img, "none")
# evaluate_edge_case(test_img, "heavy_jpeg")
# evaluate_edge_case(test_img, "downscale")
