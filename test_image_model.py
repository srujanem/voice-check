from transformers import pipeline
import sys

pipe = pipeline('image-classification', model='dima806/deepfake_vs_real_image_detection')
# Let's test it on a dummy image, or just print the id2label mapping
print('Model Labels:', pipe.model.config.id2label)
