import json

from timer.const import EXERCISE_JSON
from timer.training import Training


def add_exercise_to_json(exercise, name, overwrite=False):
    print(EXERCISE_JSON)
    with open(EXERCISE_JSON, "r+") as file:
        data = json.load(file)
        if not overwrite and name in list(data.keys()):
            raise KeyError(f"Not allowed to overwrite {name}")
        data[name] = exercise
        print(data)
        file.seek(0)
        json.dump(data, file, indent=4, sort_keys=True)


#add_exercise_to_json(Pause, Training.Pause)
#add_exercise_to_json(Init, Training.Init)

#add_exercise_to_json({"duration": 30}, Training.WIDE_PULL_UPS)
#add_exercise_to_json({"duration": 30}, Training.BACK_ROWS)


#add_exercise_to_json({"duration": 30},Training.WIDE_PUSH_UPS)
#add_exercise_to_json({"duration": 30}, Training.PUSH_UPS)