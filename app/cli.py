import json
import sys

from automation import Automation, minimize, determinate
from helpers import SimpleNamespaceEncoder
from loguru import logger


if __name__ == '__main__':
    try:
        input_file = open(sys.argv[1], 'r')
    except OSError:
        logger.exception("Can't open input json file")
        sys.exit(1)

    try:
        fa = json.load(input_file, object_hook=lambda d: Automation(**d))
    except json.JSONDecodeError:
        logger.exception("Input json parsing error")
        sys.exit(1)

    try:
        dfa = minimize(determinate(fa))
    except Exception:
        logger.exception("There was an error during automate processing")
        sys.exit(1)

    try:
        output_file = open(sys.argv[2], 'w')
    except OSError:
        logger.exception("Can't open output json file")
        sys.exit(1)

    json.dump(dfa, output_file, indent=4, cls=SimpleNamespaceEncoder)
