"""Simple pydantic configuration loader for the Pac-Man project."""

import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

DEFAULT_SIZES = [15, 15, 17, 17, 19, 19, 21, 21, 23, 25]
MIN_LEVELS = 10


class LevelConfig(BaseModel):
    """Size of one maze."""

    model_config = ConfigDict(validate_assignment=True)
    width: int = Field(default=15, ge=5, le=100, strict=True)
    height: int = Field(default=15, ge=5, le=100, strict=True)


class GameSettings(BaseModel):
    """General game parameters."""

    model_config = ConfigDict(validate_assignment=True)
    level_max_time: int = Field(default=90, ge=1, le=3600, strict=True)
    seed: int = Field(default=42, ge=0, strict=True)
    levels: list[LevelConfig] = Field(
        default_factory=lambda: [
            LevelConfig(width=s, height=s) for s in DEFAULT_SIZES
        ]
    )


class PlayerConfig(BaseModel):
    """Player parameters."""

    model_config = ConfigDict(validate_assignment=True)
    lives: int = Field(default=3, ge=1, le=99, strict=True)


class ScoreConfig(BaseModel):
    """Points per event."""

    model_config = ConfigDict(validate_assignment=True)
    pacgum: int = Field(default=10, ge=0, strict=True)
    super_pacgum: int = Field(default=50, ge=0, strict=True)
    ghost: int = Field(default=200, ge=0, strict=True)


class Config(BaseModel):
    """Whole game configuration. Use Config.start(filename)."""

    model_config = ConfigDict(validate_assignment=True)
    highscore_filename: str = Field(default="highscores.json",
                                    min_length=1, strict=True)
    game_settings: GameSettings = Field(default_factory=GameSettings)
    player: PlayerConfig = Field(default_factory=PlayerConfig)
    score: ScoreConfig = Field(default_factory=ScoreConfig)

    @classmethod
    def start(cls, filename: str) -> "Config":
        """Entry point: read the file and build the config step by step."""
        data = cls.read_file(filename)
        config = cls()
        cls.set_highscore(config, data)
        cls.set_game_settings(config, data)
        cls.fill(config.player, data.get("player"), "player")
        cls.fill(config.score, data.get("score"), "score")
        return config

    @classmethod
    def read_file(cls, filename: str) -> dict[str, Any]:
        """Return the file content as a dict, or {} if it cannot be used."""
        try:
            with open(filename, "r", encoding="utf-8") as file:
                data = json.loads(cls.remove_comments(file.read()))
        except (OSError, UnicodeDecodeError) as error:
            print(f"Warning: cannot read '{filename}': {error}")
            return {}
        except json.JSONDecodeError as error:
            print(f"Warning: invalid JSON in '{filename}' "
                  f"(line {error.lineno})")
            return {}
        if not isinstance(data, dict):
            print("Warning: config root must be a JSON object")
            return {}
        return data

    @classmethod
    def set_highscore(cls, config: "Config", data: dict[str, Any]) -> None:
        """Read the highscore filename."""
        if "highscore_filename" not in data:
            return
        try:
            config.highscore_filename = data["highscore_filename"]
        except ValidationError:
            print("Warning: 'highscore_filename' invalid, using default")

    @classmethod
    def set_game_settings(cls, config: "Config",
                          data: dict[str, Any]) -> None:
        """Read game_settings and the levels list."""
        raw_settings = data.get("game_settings")
        if not isinstance(raw_settings, dict):
            print("Warning: 'game_settings' missing or invalid")
            return
        without_levels = {k: v for k, v in raw_settings.items()
                          if k != "levels"}
        cls.fill(config.game_settings, without_levels, "game_settings")
        config.game_settings.levels = cls.load_levels(
            raw_settings.get("levels"))

    @classmethod
    def load_levels(cls, raw: Any) -> list[LevelConfig]:
        """Build the levels list: fix bad levels, at least MIN_LEVELS."""
        levels: list[LevelConfig] = []
        if isinstance(raw, list):
            for index, item in enumerate(raw):
                level = LevelConfig()
                cls.fill(level, item, f"levels[{index}]")
                levels.append(level)
        else:
            print("Warning: 'levels' missing or invalid, using defaults")
        while len(levels) < MIN_LEVELS:
            size = DEFAULT_SIZES[len(levels)]
            levels.append(LevelConfig(width=size, height=size))
        return levels

    @classmethod
    def fill(cls, obj: BaseModel, raw: Any, label: str) -> None:
        """Set each key from raw on obj; bad keys keep their default."""
        if not isinstance(raw, dict):
            print(f"Warning: '{label}' missing or invalid, using defaults")
            return
        for key, value in raw.items():
            if key not in type(obj).model_fields:
                continue  # unknown keys are ignored
            try:
                setattr(obj, key, value)
            except ValidationError as error:
                message = error.errors()[0]["msg"]
                print(f"Warning: '{label}.{key}' invalid ({message}), "
                      "using default")

    @classmethod
    def remove_comments(cls, data: str) -> str:
        """Remove #, // and /* */ comments, keeping strings and newlines."""
        """Blank out lines that start with '#'."""
        lines = data.splitlines()
        for i, line in enumerate(lines):
            if line.lstrip().startswith("#"):
                lines[i] = ""
        return "\n".join(lines)
        # result: list[str] = []
        # i = 0
        # is_string = False
        # escaped = False
        # while i < len(data):
        #     ch = data[i]
        #     next_ch = data[i + 1] if i + 1 < len(data) else ""
        #     if is_string:
        #         result.append(ch)
        #         if escaped:
        #             escaped = False
        #         elif ch == "\\":
        #             escaped = True
        #         elif ch == '"':
        #             is_string = False
        #         i += 1
        #     elif ch == '"':
        #         is_string = True
        #         result.append(ch)
        #         i += 1
        #     elif ch == "#" or (ch == "/" and next_ch == "/"):
        #         while i < len(data) and data[i] != "\n":
        #             i += 1
        #     elif ch == "/" and next_ch == "*":
        #         i += 2
        #         while i < len(data) and data[i:i + 2] != "*/":
        #             if data[i] == "\n":
        #                 result.append("\n")
        #             i += 1
        #         i += 2
        #     else:
        #         result.append(ch)
        #         i += 1
        # return "".join(result)
