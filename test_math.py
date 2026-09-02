tf_pred = 0.9323934316635132 # from earlier diagnostic (TF Fake Pred)
vit_pred = 0.0004995324416086078 # from earlier diagnostic (ViT Fake Pred)
print(f"TF says: {tf_pred}")
print(f"ViT says: {vit_pred}")
print("--- Old Math ---")
print(f"Average: {(tf_pred + vit_pred)/2}")
print("--- New Math ---")
# TF is 1.0=Fake, 0.0=Real
# ViT is 0.0=Fake, 1.0=Real
# We must invert one of them before averaging!
vit_inverted = 1.0 - vit_pred
final = (tf_pred + vit_inverted) / 2.0
print(f"Correct Average (AI probability): {final}")
