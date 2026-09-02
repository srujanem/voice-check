import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
import torch
import os
import timm
import torch.nn as nn
from transformers import ViTModel

print("=======================================")
print("  AUTHGUARD ONNX COMPILER")
print("=======================================")

device = torch.device("cpu") # ONNX export is safer on CPU

# 1. Convert the original ViT Model
vit_path = "model_image_vit_best.pth"
if os.path.exists(vit_path):
    print(f"Loading {vit_path} for ONNX conversion...")
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
            
    vit_model = DeepfakeViT()
    vit_model.load_state_dict(torch.load(vit_path, map_location=device, weights_only=True))
    vit_model.eval()
    
    dummy_input = torch.randn(1, 3, 224, 224)
    vit_onnx_path = "model_image_vit_best.onnx"
    
    torch.onnx.export(
        vit_model, 
        dummy_input, 
        vit_onnx_path, 
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    )
    print(f"SUCCESS: Saved {vit_onnx_path}")

# 2. Convert the new ConvNeXt Pro Model
convnext_path = "model_image_convnext_pro.pth"
if os.path.exists(convnext_path):
    print(f"Loading {convnext_path} for ONNX conversion...")
    class ConvNextPro(nn.Module):
        def __init__(self):
            super().__init__()
            self.backbone = timm.create_model('convnextv2_base.fcmae_ft_in22k_in1k', pretrained=False, num_classes=0)
            self.classifier = nn.Sequential(
                nn.Dropout(0.4),
                nn.Linear(self.backbone.num_features, 256),
                nn.GELU(),
                nn.Dropout(0.2),
                nn.Linear(256, 1)
            )
        def forward(self, x):
            return self.classifier(self.backbone(x))
            
    convnext_model = ConvNextPro()
    convnext_model.load_state_dict(torch.load(convnext_path, map_location=device, weights_only=True))
    convnext_model.eval()
    
    dummy_input_highres = torch.randn(1, 3, 256, 256)
    convnext_onnx_path = "model_image_convnext_pro.onnx"
    
    torch.onnx.export(
        convnext_model, 
        dummy_input_highres, 
        convnext_onnx_path, 
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    )
    print(f"SUCCESS: Saved {convnext_onnx_path}")
    
print("ONNX Compilation Complete! Inference will now be ~10x faster.")
