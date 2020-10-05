import json
from minimizer import minimize, determinater
import sys

if __name__ == '__main__':
    with open(sys.argv[1], 'r') as f:
        dfa = json.load(f)
    with open(sys.argv[2], 'w') as f:
        json.dump(minimize(determinater(dfa)), f, indent=4)
