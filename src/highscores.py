"""Persistent top-10 highscores stored in a JSON file."""
import json
from typing import Any

MAX_ENTRIES = 10
MAX_NAME_LENGTH = 10
DEFAULT_NAME = "PLAYER"


class Highscores:
    """
    Load, keep and save the top 10 scores.
    The file is a JSON list of {"name": str, "score": int}
    """

    def __init__(self, filename: str) -> None:
        """Create the table and load it from `filename`."""
        self.filename = filename
        self.entries: list[tuple[str, int]] = []
        self.load()

    @staticmethod
    def is_valid_char(char: str) -> bool:
        """Return True if `char` is allowed in a player name."""
        return len(char) == 1 and char.isascii() and (
            char.isalnum() or char == " ")

    @classmethod
    def clean_name(cls, name: str) -> str:
        """Keep only allowed characters, max 10 of them."""
        cleaned = "".join(c for c in name if cls.is_valid_char(c))
        cleaned = cleaned.strip()[:MAX_NAME_LENGTH].strip()
        return cleaned if cleaned else DEFAULT_NAME

    def load(self) -> None:
        """Read the highscore file; keep only valid entries."""
        self.entries = []
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                data: Any = json.load(file)
        except FileNotFoundError:
            return  # first run: no highscores yet
        except (OSError, UnicodeDecodeError) as error:
            print(f"Warning: cannot read highscores '{self.filename}': "
                  f"{error}")
            return
        except json.JSONDecodeError:
            print(f"Warning: highscores file '{self.filename}' is not "
                  "valid JSON, starting with an empty table.")
            return

        if not isinstance(data, list):
            print("Warning: highscores file must contain a list, "
                  "starting with an empty table.")
            return
        for item in data:
            if not isinstance(item, dict):
                continue
            name = item.get("name")
            score = item.get("score")
            if (not isinstance(name, str) or not isinstance(score, int)
                    or isinstance(score, bool) or score < 0):
                continue
            self.entries.append((self.clean_name(name), score))
        self.sort()

    def save(self) -> None:
        """Write the table to disk; report errors without crashing."""
        data = [{"name": n, "score": s} for n, s in self.entries]
        try:
            with open(self.filename, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)
        except OSError as error:
            print(f"Warning: cannot save highscores '{self.filename}': "
                  f"{error}")

    def sort(self) -> None:
        """Sort by score (best first) and keep the top 10."""
        self.entries.sort(key=lambda entry: entry[1], reverse=True)
        del self.entries[MAX_ENTRIES:]

    def add(self, name: str, score: int) -> None:
        """Add a score, keep the top 10 and save the file."""
        self.entries.append((self.clean_name(name), max(0, int(score))))
        self.sort()
        self.save()
