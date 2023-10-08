from jdots import jdots
import json

tmp = {
    "foo": "thing",
    "foo2": {
        "subfoo": {"subsubfoo": False, "subsubfoo2": 1234102134, "subsubfoo3": 3.082},
    },
    "foo3": [
        {"foo": "flarp"},
        {"foo": "flink"},
        {"faa": "fleerg"},
        {"flip": "fleegan"},
    ],
}

foo = jdots()

dotted = foo.flatten(tmp, "$")

print("------------------------------------------")
print("From dictionary...")
print("------------------------------------------")
print(dotted)

tmpJson = None

tmpJson = json.dumps(tmp)

dotted2 = foo.flatten(tmpJson, "")

print("------------------------------------------")
print("From string...")
print("------------------------------------------")
print(dotted2)
