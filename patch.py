with open("train_image_advanced.py", "r") as f:
    code = f.read()

code = code.replace("epochs=3", "epochs=5, class_weight=class_weight")
code = code.replace("epochs=5\n", "epochs=5, class_weight=class_weight\n") # if there was another one

with open("train_image_advanced.py", "w") as f:
    f.write(code)
