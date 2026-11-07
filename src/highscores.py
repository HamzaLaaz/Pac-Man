import json
from typing import Any


class Highscores:
    """
    Load, keep and save the top 10 scores.
    The file is a JSON list of {"name": str, "score": int}
    """

    def __init__(self, filename: str) -> None:
        """Create the table and load it from `filename`."""
        self.filename = filename
        self.entries: list[tuple[str, int]] = []

    @staticmethod
    def is_valid_char(char: str) -> bool:
        """Return True if `char` is allowed in a player name."""
        if (len(char) == 1 and char.isascii() and (
            char.isalnum() or char == " ")):
            return True
        return False

    @classmethod
    def clean_name(cls, name: str) -> str:
        """Keep only allowed characters, max 10 of them."""
        cleaned = "".join(c for c in name if cls.is_valid_char(c))
        cleaned = cleaned.strip()[:10].strip()
        return cleaned if cleaned else "PLAYER"

    def _add_unique(self, cleaned_name: str, score: int) -> bool:
        """Helper to append an entry only if (name, score) is not already present."""
        entry = (cleaned_name, score)
        if entry not in self.entries:
            self.entries.append(entry)
            return True
        return False

    def load_file(self) -> None:
        """Read the highscore file; keep only valid entries."""
        self.entries = []
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                data: Any = json.load(file)
        except FileNotFoundError:
            return  # first run: no highscores yet
        except OSError as error:
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
        file_had_duplicates = False
        for item in data:
            if not isinstance(item, dict):
                continue
            name = item.get("name")
            score = item.get("score")
            if (not isinstance(name, str) or not isinstance(score, int)
                    or isinstance(score, bool) or score < 0):
                continue
            cleaned = self.clean_name(name)
            if not self._add_unique(cleaned, score):
                file_had_duplicates = True
        self.sort_highscores()
        if file_had_duplicates:
            self.save_table()

    def save_table(self) -> None:
        """Write the table to disk; report errors without crashing."""
        data = [{"name": n, "score": s} for n, s in self.entries]
        try:
            with open(self.filename, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)
        except OSError as error:
            print(f"Warning: cannot save highscores '{self.filename}': "
                  f"{error}")

    def sort_highscores(self) -> None:
        """Sort by score (best first) and keep the top 10."""
        self.entries.sort(key=lambda entry: entry[1], reverse=True)
        self.entries = self.entries[:10]

    def add(self, name: str, score: int) -> None:
        """Add a score if unique, keep the top 10 and save the file."""
        cleaned_name = self.clean_name(name)
        valid_score = max(0, int(score))

        if self._add_unique(cleaned_name, valid_score):
            self.sort_highscores()
            self.save_table()
