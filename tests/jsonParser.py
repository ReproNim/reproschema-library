import os
import json

tested = 0
for root, dirs, files in os.walk('activities', topdown=True):
    for name in files:
        with open(os.path.join(root, name)) as fp:
            try:
                tested +=1
                json.load(fp)
            except json.decoder.JSONDecodeError:
                print(f"{root}/{name} could not be loaded")
                raise
if tested == 0:
    raise ValueError("Zero files tested")

