"""
VoiceShield — Audio AI vs Human Classifier
Architecture: Wav2Vec2-base fine-tuned for binary classification
Optimized for RTX 4050 with 6GB VRAM
"""
import torch
import torch.nn as nn
from transformers import Wav2Vec2Model, Wav2Vec2Config


class VoiceShieldModel(nn.Module):
    """
    Binary classifier: AI Voice vs Human Voice
    Based on Wav2Vec2-base with custom classification head
    """
    def __init__(self, num_labels: int = 2, dropout: float = 0.3, freeze_feature_extractor: bool = True):
        super().__init__()

        # Load pretrained Wav2Vec2 backbone
        self.wav2vec2 = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base")

        # Freeze feature extractor (CNN layers) to save VRAM
        if freeze_feature_extractor:
            for param in self.wav2vec2.feature_extractor.parameters():
                param.requires_grad = False

        # Only fine-tune last 4 transformer layers
        for i, layer in enumerate(self.wav2vec2.encoder.layers):
            if i < len(self.wav2vec2.encoder.layers) - 4:
                for param in layer.parameters():
                    param.requires_grad = False

        hidden_size = self.wav2vec2.config.hidden_size  # 768 for base

        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size, 512),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.LayerNorm(512),
            nn.Linear(512, 256),
            nn.GELU(),
            nn.Dropout(dropout / 2),
            nn.Linear(256, num_labels)
        )

        # Attention pooling layer
        self.attention_pool = nn.Sequential(
            nn.Linear(hidden_size, 1),
            nn.Softmax(dim=1)
        )

    def forward(self, input_values: torch.Tensor, attention_mask: torch.Tensor = None) -> torch.Tensor:
        outputs = self.wav2vec2(input_values=input_values, attention_mask=attention_mask)
        hidden_states = outputs.last_hidden_state  # (batch, seq_len, 768)

        # Attention pooling instead of mean pooling
        attn_weights = self.attention_pool(hidden_states)  # (batch, seq_len, 1)
        pooled = (hidden_states * attn_weights).sum(dim=1)  # (batch, 768)

        logits = self.classifier(pooled)
        return logits

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
    model = VoiceShieldModel()
    params = model.count_parameters()
    print(f"VoiceShield Model:")
    print(f"  Total params:     {params['total']:,}")
    print(f"  Trainable params: {params['trainable']:,} ({params['trainable_pct']}%)")
    print(f"  Frozen params:    {params['frozen']:,}")

    # Test forward pass
    dummy = torch.randn(2, 16000)  # 1 second of audio at 16kHz
    logits = model(dummy)
    print(f"  Output shape: {logits.shape}")
    probs = torch.softmax(logits, dim=-1)
    print(f"  Probabilities: {probs.detach().numpy()}")
