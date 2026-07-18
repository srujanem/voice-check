"""
PixelGuard — Image AI vs Human Classifier
Architecture: EfficientNet-B4 + FFT artifact detector
Optimized for RTX 4050 with 6GB VRAM
"""
import torch
import torch.nn as nn
import timm
import numpy as np


class FrequencyAnalysisModule(nn.Module):
    """
    Detects GAN/Diffusion fingerprints in the frequency domain
    AI-generated images often have characteristic patterns in FFT
    """
    def __init__(self, out_features: int = 64):
        super().__init__()
        self.conv_layers = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(4)
        )
        self.fc = nn.Linear(64 * 16, out_features)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Apply 2D FFT and use magnitude spectrum
        # x: (B, 3, H, W)
        gray = x.mean(dim=1, keepdim=True).repeat(1, 3, 1, 1)
        fft = torch.fft.fft2(gray)
        magnitude = torch.log(torch.abs(fft) + 1e-8)
        magnitude = magnitude - magnitude.min()
        magnitude = magnitude / (magnitude.max() + 1e-8)

        feat = self.conv_layers(magnitude)
        feat = feat.view(feat.size(0), -1)
        return self.fc(feat)


class PixelGuardModel(nn.Module):
    """
    Binary classifier: AI Image vs Human Photo
    EfficientNet-B4 backbone + Frequency domain analysis
    """
    def __init__(
        self,
        num_labels: int = 2,
        dropout: float = 0.3,
        use_frequency_module: bool = True,
        freeze_backbone_stages: int = 5  # Freeze first N stages
    ):
        super().__init__()
        self.use_frequency_module = use_frequency_module

        # EfficientNet-B4 backbone
        self.backbone = timm.create_model(
            "efficientnet_b4",
            pretrained=True,
            num_classes=0,  # Remove classification head
            global_pool="avg"
        )

        # Freeze early stages to save VRAM
        stages = list(self.backbone.children())
        for i, stage in enumerate(stages):
            if i < freeze_backbone_stages:
                for param in stage.parameters():
                    param.requires_grad = False

        backbone_features = self.backbone.num_features  # 1792 for B4

        # Optional frequency analysis branch
        freq_features = 0
        if use_frequency_module:
            self.freq_module = FrequencyAnalysisModule(out_features=64)
            freq_features = 64

        total_features = backbone_features + freq_features

        # Final classifier
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(total_features, 512),
            nn.GELU(),
            nn.BatchNorm1d(512),
            nn.Dropout(dropout / 2),
            nn.Linear(512, 128),
            nn.GELU(),
            nn.Linear(128, num_labels)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Main branch: EfficientNet features
        backbone_feat = self.backbone(x)  # (B, 1792)

        if self.use_frequency_module:
            freq_feat = self.freq_module(x)  # (B, 64)
            combined = torch.cat([backbone_feat, freq_feat], dim=1)  # (B, 1856)
        else:
            combined = backbone_feat

        return self.classifier(combined)

    def count_parameters(self) -> dict:
        total = sum(p.numel() for p in self.parameters())
        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        return {
            "total": total,
            "trainable": trainable,
            "frozen": total - trainable,
            "trainable_pct": round(trainable / total * 100, 2)
        }


if __name__ == "__main__":
    model = PixelGuardModel()
    params = model.count_parameters()
    print(f"PixelGuard Model:")
    print(f"  Total params:     {params['total']:,}")
    print(f"  Trainable params: {params['trainable']:,} ({params['trainable_pct']}%)")

    dummy = torch.randn(2, 3, 380, 380)
    logits = model(dummy)
    print(f"  Output shape: {logits.shape}")
    probs = torch.softmax(logits, dim=-1)
    print(f"  Probabilities: {probs.detach().numpy()}")
