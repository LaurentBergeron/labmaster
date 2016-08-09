import os, glob
import pickle
import mod.classes
import copy

for folder in glob.glob("C:/Data/2016/LabMasterData/params/*"):
    for filename in glob.glob(folder+"/*"):
        if filename.endswith(".pickle"):
            try:
                with open(filename, "rb") as f:
                    params = pickle.load(f)
                new_params = mod.classes.Params()
                if not hasattr(params, "object_type"):
                    new_params.object_type = params.class_type
                for key, param in params.get_items():
                    new_params.__dict__[key] = copy.deepcopy(param)
                print new_params.get_names()
                with open(filename, "wb") as f:
                    pickle.dump(new_params, f, pickle.HIGHEST_PROTOCOL)
            except:
                # raise
                print filename
                
