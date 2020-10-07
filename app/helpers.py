import json

class SimpleNamespaceEncoder(json.JSONEncoder):
    def default(self, o):
        return vars(o)
