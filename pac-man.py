import sys
from src import start

if __name__ == "__main__":
    if len(sys.argv) != 2:
        start.main("config.json")
    else:
        start.main(sys.argv[1])
