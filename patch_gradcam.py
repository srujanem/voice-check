import os
import re

filepath = r'D:\voice-check\voice-check\backend\routes\image_routes.py'
with open(filepath, 'r') as f:
    content = f.read()

new_func = '''def generate_gradcam(img_array, model, last_conv_layer_name="efficientnetb0"):
    import tensorflow as tf
    try:
        last_conv_layer = model.get_layer(last_conv_layer_name)
        last_conv_layer_model = tf.keras.Model(last_conv_layer.inputs, last_conv_layer.output)
        
        classifier_input = tf.keras.Input(shape=last_conv_layer.output.shape[1:])
        x = classifier_input
        for layer_name in ["global_average_pooling2d", "dropout", "dense", "dropout_1", "dense_1"]:
            try:
                x = model.get_layer(layer_name)(x)
            except:
                pass
        classifier_model = tf.keras.Model(classifier_input, x)
        
        with tf.GradientTape() as tape:
            last_conv_layer_output = last_conv_layer_model(img_array)
            tape.watch(last_conv_layer_output)
            preds = classifier_model(last_conv_layer_output)
            class_channel = 1.0 - preds[0][0]
            
        grads = tape.gradient(class_channel, last_conv_layer_output)
        if grads is None: return None
        
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        last_conv_layer_output = last_conv_layer_output[0]
        heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
        return heatmap.numpy()
    except Exception as e:
        print("GradCAM Generation Failed:", e)
        return None'''

# Replace the existing function
content = re.sub(r'def generate_gradcam.*?return heatmap\.numpy\(\)', new_func, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)

print("Patched GradCAM.")
