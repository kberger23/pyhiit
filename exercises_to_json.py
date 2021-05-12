import json

from timer.const import EXERCISE_JSON


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

Pause = dict()
Pause["duration"] = 7
#add_exercise_to_json(Pause, "Pause")

Init = dict()
Init["duration"] = 10
#add_exercise_to_json(Init, "Init")

#add_exercise_to_json({"duration": 30}, "Wide pull-ups")
#add_exercise_to_json({"duration": 30}, "Back rows")

#add_exercise_to_json({"duration": 30}, "Wide push-ups")
#add_exercise_to_json({"duration": 30}, "Push-ups")