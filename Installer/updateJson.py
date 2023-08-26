import json

def updateJson(json_filepath, path_value_pairs):
    with open(json_filepath, 'r+') as file:
        data = json.load(file)

        for path, value in path_value_pairs.items():
            keys = path.split('.')
            current = data
            for key in keys[:-1]:
                current = current[key]
            current[keys[-1]] = value

        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()

