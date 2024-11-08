import os
import json

tested = 0
for root, dirs, files in os.walk('activities', topdown=True):
    for name in files:
        filename = os.path.join(root, name)
        with open(filename) as fp:
            try:
                tested +=1
                data = json.load(fp)
                if "@id" in data:
                    str_id = "@id"
                elif "id" in data:
                    str_id = "id"
                else:
                    raise ValueError(f"{root}/{name} does not have @id")
                if data[str_id] != name:
                    raise ValueError(f"{root}/{name} does not have matching @id to name")
            except json.decoder.JSONDecodeError:
                print(f"{root}/{name} could not be loaded")
                raise
if tested == 0:
    raise ValueError("Zero files tested")
