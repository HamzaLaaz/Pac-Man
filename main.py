import sys
from src.config import Config

def main() -> int:
    try:
        config = Config.start(sys.argv[1])
        print(config)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    # ... start the game with `config`
    return 0

if __name__ == "__main__":
    sys.exit(main())

with open("src/config.json", "r") as file:
    print(file.read())
