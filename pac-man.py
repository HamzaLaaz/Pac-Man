import sys
from src import start

if __name__ == "__main__":
    if len(sys.argv) == 2:
        start.main(sys.argv[1])
    else:
        sys.exit(print("Usage: python3 pac-man.py <config.json>"))
