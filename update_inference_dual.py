import os

with open(r"D:\Server\ai-training-panel\python_engine\inference.py", "r", encoding="utf-8") as f:
    script = f.read()

old_image_func = """def run_image_inference(file_path):
    try:
        import tensorflow as tf
        from PIL import Image
        import numpy as np
        
        model_path = os.path.join(os.path.dirname(__file__), "../../voice-check/voice-check/model_image_best_grid.keras")
        if not os.path.exists(model_path):
             return {"error": "Image model not found. Please run: python train_deep.py"}
        
        model = tf.keras.models.load_model(model_path)
        
        img = Image.open(file_path).convert('RGB')
        img = img.resize((224, 224))
        
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        prediction = model.predict(img_array)[0][0]
        
        # 1.0 = Fake, 0.0 = Real
        is_fake = float(prediction) > 0.5
        confidence = float(prediction) if is_fake else float(1.0 - prediction)
        
        return {
            "label": "Fake" if is_fake else "Human",
            "score": confidence
        }
    except Exception as e:
        return {"error": str(e)}"""

new_image_func = """def run_image_inference(file_path):
    try:
        import tensorflow as tf
        from PIL import Image
        import numpy as np
        import torch
        from torchvision import transforms
        from transformers import ViTModel
        import torch.nn as nn
        
        # --- ENGINE 1: TENSORFLOW EFFICIENTNET ---
        tf_model_path = os.path.join(os.path.dirname(__file__), "../../voice-check/voice-check/model_image_best_grid.keras")
        if not os.path.exists(tf_model_path):
             return {"error": "Image model not found. Please run: python train_deep.py"}
        
        tf_model = tf.keras.models.load_model(tf_model_path)
        img = Image.open(file_path).convert('RGB')
        img_tf = img.resize((224, 224))
        img_array = np.array(img_tf) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        tf_prediction = float(tf_model.predict(img_array, verbose=0)[0][0])
        
        # --- ENGINE 2: PYTORCH VISION TRANSFORMER (If Available) ---
        vit_model_path = os.path.join(os.path.dirname(__file__), "../../voice-check/voice-check/model_image_vit_best.pth")
        
        if os.path.exists(vit_model_path):
            class DeepfakeViT(nn.Module):
                def __init__(self):
                    super().__init__()
                    self.vit = ViTModel.from_pretrained('google/vit-base-patch16-224-in21k')
                    self.classifier = nn.Sequential(
                        nn.Linear(self.vit.config.hidden_size, 256),
                        nn.ReLU(),
                        nn.Dropout(0.3),
                        nn.Linear(256, 1)
                    )
                def forward(self, pixel_values):
                    outputs = self.vit(pixel_values=pixel_values)
                    return self.classifier(outputs.pooler_output)

            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            vit_model = DeepfakeViT().to(device)
            vit_model.load_state_dict(torch.load(vit_model_path, map_location=device))
            vit_model.eval()

            transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
            ])
            img_pt = transform(img).unsqueeze(0).to(device)
            with torch.no_grad():
                vit_logits = vit_model(img_pt)
                vit_prediction = float(torch.sigmoid(vit_logits).cpu().item())
                
            # DUAL-ENGINE ENSEMBLE AVERAGING
            final_prediction = (tf_prediction + vit_prediction) / 2.0
            print(f"[DUAL ENGINE] TF Score: {tf_prediction:.3f} | ViT Score: {vit_prediction:.3f} | Final: {final_prediction:.3f}")
        else:
            final_prediction = tf_prediction
            print(f"[SINGLE ENGINE] TF Score: {tf_prediction:.3f}")
        
        # 1.0 = Fake, 0.0 = Real
        is_fake = final_prediction > 0.5
        confidence = float(final_prediction) if is_fake else float(1.0 - final_prediction)
        
        return {
            "label": "Fake" if is_fake else "Human",
            "score": confidence
        }
    except Exception as e:
        return {"error": str(e)}"""

if old_image_func in script:
    script = script.replace(old_image_func, new_image_func)
    with open(r"D:\Server\ai-training-panel\python_engine\inference.py", "w", encoding="utf-8") as f:
        f.write(script)
    print("Inference engine successfully upgraded to Dual-Engine Architecture!")
else:
    print("Could not find the exact old function to replace. It might have been modified.")
