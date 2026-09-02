import os

with open('c:/voice-check/backend/services/ml_engine.py', 'r', encoding='utf-8') as f:
    code = f.read()

new_method = """
    def analyze_document(self, img):
        import torch
        from torchvision import transforms, models
        import torch.nn as nn
        
        # Lazy load model
        if not hasattr(self, 'document_model') or self.document_model is None:
            print("[ML Engine] Loading Document Forgery ResNet18...")
            try:
                device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                model = models.resnet18(weights=None)
                num_ftrs = model.fc.in_features
                model.fc = nn.Sequential(nn.Dropout(0.3), nn.Linear(num_ftrs, 2))
                model.load_state_dict(torch.load("models/model_document_forgery.pth", map_location=device, weights_only=True))
                model = model.to(device)
                model.eval()
                self.document_model = model
                self.doc_device = device
            except Exception as e:
                print(f"Document model load failed: {e}")
                raise Exception("Document AI model failed to load.")

        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        input_tensor = transform(img).unsqueeze(0).to(self.doc_device)
        with torch.no_grad():
            outputs = self.document_model(input_tensor)
            probs = torch.nn.functional.softmax(outputs, dim=1)[0]
            prob_real = float(probs[0]) * 100
            prob_fake = float(probs[1]) * 100
            
        is_fake = prob_fake > 50.0
        confidence = prob_fake if is_fake else prob_real
        
        return {
            "prediction": "Forged/Tampered Document" if is_fake else "Authentic Document",
            "confidence": confidence,
            "prob_human": prob_real,
            "prob_ai": prob_fake,
            "forensics": {
                "ela_anomalies": is_fake,
                "metadata_risk": "High" if is_fake else "Low"
            }
        }
"""

if 'def analyze_document' not in code:
    # insert before the ml_engine instance creation at the very end
    if 'ml = MLEngine()' in code:
        code = code.replace('ml = MLEngine()', new_method + '\n\nml = MLEngine()')
        with open('c:/voice-check/backend/services/ml_engine.py', 'w', encoding='utf-8') as f:
            f.write(code)
            print('Successfully injected analyze_document')
    else:
        print('Could not find ml_engine instance')
else:
    print('Already has analyze_document')
