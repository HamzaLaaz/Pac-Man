import json
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, ValidationError

DEFAULT_SIZES = [15, 17, 17, 19, 19, 21, 21, 23, 25, 28]
MIN_LEVELS = 10
MAX_FIX_ROUNDS = 50


class LevelConfig(BaseModel):
    """Size of one maze."""
    model_config = ConfigDict(extra="ignore")
    width: int = Field(default=15, ge=5, le=29)
    height: int = Field(default=15, ge=5, le=29)


class GameSettings(BaseModel):
    """General game parameters."""
    model_config = ConfigDict(extra="ignore")
    level_max_time: int = Field(default=90, ge=1, le=3600)
    seed: int = Field(default=42, ge=0)
    levels: list[LevelConfig] = Field(
        default_factory=lambda: [
            LevelConfig(width=s, height=s) for s in DEFAULT_SIZES]
    )


class PlayerConfig(BaseModel):
    """Player parameters."""
    model_config = ConfigDict(extra="ignore")
    lives: int = Field(default=3, ge=1, le=99)


class ScoreConfig(BaseModel):
    """Points per event."""
    model_config = ConfigDict(extra="ignore")
    pacgum: int = Field(default=10, ge=0)
    super_pacgum: int = Field(default=50, ge=0)
    ghost: int = Field(default=200, ge=0)


class Config(BaseModel):
    """Whole game configuration. Use Config.start(filename)."""
    model_config = ConfigDict(extra="ignore")
    highscore_filename: str = Field(default="highscores.json", min_length=1)
    game_settings: GameSettings = Field(default_factory=GameSettings)
    player: PlayerConfig = Field(default_factory=PlayerConfig)
    score: ScoreConfig = Field(default_factory=ScoreConfig)

    @classmethod
    def start(cls, filename: str) -> "Config":
        """Entry point: read the file and build the config safely.

        Every invalid value is fixed one by one (clamped to its limit or
        replaced by its default) and a warning is printed, so one bad
        value never resets the whole configuration.
        """
        data = cls.read_file(filename)
        cls.fill_levels(data)

        for _ in range(MAX_FIX_ROUNDS):
            try:
                return cls.model_validate(data)
            except ValidationError as error:
                for err in error.errors():
                    cls.fix_value(data, err)
            except Exception as error:
                print(f"Warning: invalid configuration ({error}), "
                      "using default values.")
                return cls()
        print("Warning: configuration could not be repaired, "
              "using default values.")
        return cls()

    @staticmethod
    def fill_levels(data: dict[str, Any]) -> None:
        """Add default levels until there are at least MIN_LEVELS."""
        settings = data.get("game_settings")
        if not isinstance(settings, dict):
            return
        raw_levels = settings.get("levels")
        if not isinstance(raw_levels, list):
            return
        if len(raw_levels) < MIN_LEVELS:
            print(f"Warning: config has {len(raw_levels)} levels, "
                  f"adding default levels up to {MIN_LEVELS}.")
        while len(raw_levels) < MIN_LEVELS:
            idx = len(raw_levels)
            size = DEFAULT_SIZES[idx] if idx < len(DEFAULT_SIZES) else 28
            raw_levels.append({"width": size, "height": size})

    @staticmethod
    def fix_value(data: dict[str, Any], err: Any) -> None:
        """Clamp or remove the value described by a pydantic error."""
        loc = err.get("loc", ())
        if not loc:
            data.clear()
            return
        name = ".".join(str(part) for part in loc)
        parent: Any = data
        try:
            for part in loc[:-1]:
                parent = parent[part]
            last = loc[-1]
            value = parent[last]
        except (KeyError, IndexError, TypeError):
            # The parent itself is broken: drop the top-level key.
            data.pop(loc[0], None)
            print(f"Warning: config '{loc[0]}' is invalid, using defaults.")
            return

        ctx = err.get("ctx") or {}
        kind = err.get("type", "")
        if kind in ("greater_than_equal", "greater_than") and "ge" in ctx:
            new_value: Any = ctx["ge"]
        elif kind in ("greater_than_equal", "greater_than") and "gt" in ctx:
            new_value = ctx["gt"] + 1
        elif kind in ("less_than_equal", "less_than") and "le" in ctx:
            new_value = ctx["le"]
        elif kind in ("less_than_equal", "less_than") and "lt" in ctx:
            new_value = ctx["lt"] - 1
        else:
            new_value = None

        if new_value is not None:
            parent[last] = new_value
            print(f"Warning: config '{name}' = {value!r} is out of range, "
                  f"clamped to {new_value}.")
        elif isinstance(parent, list):
            parent[last] = {}
            print(f"Warning: config '{name}' is invalid, using default level.")
        else:
            del parent[last]
            print(f"Warning: config '{name}' = {value!r} is invalid "
                  f"({err.get('msg', 'bad value')}), using default.")

    @classmethod
    def read_file(cls, filename: str) -> dict[str, Any]:
        """Return the file content as a dict, or {} if it cannot be used."""
        try:
            with open(filename, "r", encoding="utf-8") as file:
                clean_json = cls.remove_comments(file.read())
                data = json.loads(clean_json)
                if isinstance(data, dict):
                    return data
                print("Warning: config root must be a JSON object.")
        except (OSError, UnicodeDecodeError) as error:
            print(f"Warning: Cannot read '{filename}': {error}")
        except json.JSONDecodeError as error:
            print(f"Warning: Invalid JSON in '{filename}' "
                  f"(line {error.lineno})")
        return {}

    @staticmethod
    def remove_comments(data: str) -> str:
        """Remove #, // and /* */ comments using basic loops and conditions."""
        result = []
        i = 0
        length = len(data)
        is_string = False
        while i < length:
            # 1. Handle inside quoted strings (ignore comments inside "...")
            if is_string:
                result.append(data[i])
                if data[i] == '"' and data[i - 1] != '\\':
                    is_string = False
                i += 1
                continue
            # Check for string start
            if data[i] == '"':
                is_string = True
                result.append(data[i])
                i += 1
                continue
            # 2. Handle single-line comments (# or //)
            if data[i] == '#' or (data[i:i + 2] == '//'):
                # Skip characters until end of line
                while i < length and data[i] != '\n':
                    i += 1
                continue
            # 3. Handle multi-line comments (/* ... */)
            if data[i:i + 2] == '/*':
                i += 2
                # Skip characters until '*/'
                while i < length and data[i:i + 2] != '*/':
                    # Preserve newlines to keep JSON line numbers accurate
                    if data[i] == '\n':
                        result.append('\n')
                    i += 1
                i += 2  # Skip closing '*/'
                continue
            # 4. Keep normal JSON characters
            result.append(data[i])
            i += 1
        return "".join(result)
