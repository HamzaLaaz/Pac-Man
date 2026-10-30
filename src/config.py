import json
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, ValidationError

DEFAULT_SIZES = [15, 17, 17, 19, 19, 21, 21, 23, 25, 28]
MIN_LEVELS = 10


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
        default_factory=lambda: [LevelConfig(width=s, height=s) for s in DEFAULT_SIZES]
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
        """Entry point: read the file and build the config safely."""
        data = cls.read_file(filename)

        # Ensure levels array meets the minimum requirement
        if "game_settings" in data and "levels" in data["game_settings"]:
            raw_levels = data["game_settings"].get("levels", [])
            if isinstance(raw_levels, list):
                # Ensure at least 10 levels exist by filling missing ones with default sizes
                while len(raw_levels) < MIN_LEVELS:
                    idx = len(raw_levels)
                    size = DEFAULT_SIZES[idx] if idx < len(DEFAULT_SIZES) else 28
                    raw_levels.append({"width": size, "height": size})
                data["game_settings"]["levels"] = raw_levels

        try:
            return cls.model_validate(data)
        except Exception as error:
            print(f"Warning: Error parsing configuration ({error}). Using default fallback.")
            return cls()

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
            print(f"Warning: Invalid JSON in '{filename}' (line {error.lineno})")
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
