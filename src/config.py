import json
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

DEFAULT_SIZES = [15, 17, 17, 19, 19, 21, 21, 23, 25, 28]
MIN_LEVELS = 10


class LevelConfig(BaseModel):
    """Size of one maze."""
    width: int = Field(default=15, ge=5, le=29)
    height: int = Field(default=15, ge=5, le=29)


class GameSettings(BaseModel):
    """General game parameters."""
    level_max_time: int = Field(default=90, ge=1, le=3600)
    seed: int = Field(default=42, ge=0)
    levels: list[LevelConfig] = Field(
        default_factory=lambda: [
            LevelConfig(width=s, height=s) for s in DEFAULT_SIZES])


class PlayerConfig(BaseModel):
    """Player parameters."""
    lives: int = Field(default=3, ge=1, le=99)


class ScoreConfig(BaseModel):
    """Points per event."""
    pacgum: int = Field(default=10, ge=0)
    super_pacgum: int = Field(default=50, ge=0)
    ghost: int = Field(default=200, ge=0)


class Config(BaseModel):
    """Whole game configuration."""
    highscore_filename: str = Field(default="highscores.json", min_length=1)
    game_settings: GameSettings = Field(default_factory=GameSettings)
    player: PlayerConfig = Field(default_factory=PlayerConfig)
    score: ScoreConfig = Field(default_factory=ScoreConfig)

    @classmethod
    def start(cls, filename: str) -> "Config":
        """Entry point: reads file, normalizes and clamps
          all values upfront, then builds config."""
        data = cls.read_file(filename)

        # 1. validate/clamp values and fill defaults in-place before validation
        cls.validate_and_fill(data)

        # 2. Safely parse into Pydantic model without tracebacks
        try:
            return cls.model_validate(data)
        except Exception as error:
            print(f"Warning: Unexpected error loading config ({error}), "
                  "using standard default configuration.")
            return cls()

    @classmethod
    def validate_and_fill(cls, data: dict[str, Any]) -> None:
        """Normalizes sections, clamps out-of-range
          values, and fills default levels."""
        cls._validate_highscore(data)
        cls._validate_player(data)
        cls._validate_score(data)
        cls._validate_game_settings(data)

    @staticmethod
    def _clamp(val: Any, min_val: int, max_val: int, default_val: int, name: str) -> int:
        """Helper to validate type and clamp an integer to min/max bounds."""
        if not isinstance(val, int) or isinstance(val, bool):
            print(f"Warning: config '{name}' = {val} is invalid, "
                  f"using default {default_val}.")
            return default_val
        if val < min_val:
            print(f"Warning: config '{name}' = {val} is too small, "
                  f"clamped to {min_val}.")
            return default_val
        if val > max_val:
            print(f"Warning: config '{name}' = {val} is too large, "
                  f"clamped to {max_val}.")
            return default_val
        return val

    @classmethod
    def _validate_highscore(cls, data: dict[str, Any]) -> None:
        val = data.get("highscore_filename")
        if val is not None and (not isinstance(val, str) or len(val) == 0):
            print(f"Warning: config 'highscore_filename' = {val!r} is invalid, using default.")
            data.pop("highscore_filename", None)

    @classmethod
    def _validate_player(cls, data: dict[str, Any]) -> None:
        player = data.get("player")
        if not isinstance(player, dict):
            if player is not None:
                print("Warning: config 'player' section is invalid, using default.")
            data["player"] = {}
            return

        if "lives" in player:
            player["lives"] = cls._clamp(
                player["lives"],
                min_val=1, max_val=99, default_val=3, name="player.lives")

    @classmethod
    def _validate_score(cls, data: dict[str, Any]) -> None:
        score = data.get("score")
        if not isinstance(score, dict):
            if score is not None:
                print("Warning: config 'score' section is invalid, using default.")
            data["score"] = {}
            return

        for key, min_val, max_val, default_val in [
            ("pacgum", 0, 10000, 10),
            ("super_pacgum", 0, 10000, 50),
            ("ghost", 0, 10000, 200),
        ]:
            if key in score:
                score[key] = cls._clamp(score[key], min_val, max_val, default_val, f"score.{key}")

    @classmethod
    def _validate_game_settings(cls, data: dict[str, Any]) -> None:
        settings = data.get("game_settings")
        if not isinstance(settings, dict):
            if settings is not None:
                print("Warning: config 'game_settings' section is invalid, using default.")
            settings = {}
            data["game_settings"] = settings

        if "level_max_time" in settings:
            settings["level_max_time"] = cls._clamp(
                settings["level_max_time"], min_val=1, max_val=3600, default_val=90, name="game_settings.level_max_time"
            )

        if "seed" in settings:
            seed_val = settings["seed"]
            if not isinstance(seed_val, int) or isinstance(seed_val, bool) or seed_val < 0:
                print(f"Warning: config 'game_settings.seed' = {seed_val!r} is invalid, using default 42.")
                settings["seed"] = 42

        # validate and pad levels array
        raw_levels = settings.get("levels")
        if not isinstance(raw_levels, list):
            if raw_levels is not None:
                print("Warning: config 'game_settings.levels' is invalid, resetting levels list.")
            raw_levels = []
            settings["levels"] = raw_levels

        cleaned_levels = []
        for i, lvl in enumerate(raw_levels):
            if not isinstance(lvl, dict):
                print(f"Warning: config level entry #{i} is invalid, using default level dimensions.")
                lvl = {}

            w = cls._clamp(lvl.get("width", 15), min_val=5, max_val=29, default_val=15, name=f"levels[{i}].width")
            h = cls._clamp(lvl.get("height", 15), min_val=5, max_val=29, default_val=15, name=f"levels[{i}].height")
            cleaned_levels.append({"width": w, "height": h})

        # Pad remaining levels up to MIN_LEVELS
        if len(cleaned_levels) < MIN_LEVELS:
            print(f"Warning: config has {len(cleaned_levels)} levels, adding default levels up to {MIN_LEVELS}.")
            while len(cleaned_levels) < MIN_LEVELS:
                idx = len(cleaned_levels)
                size = DEFAULT_SIZES[idx] if idx < len(DEFAULT_SIZES) else 28
                cleaned_levels.append({"width": size, "height": size})

        settings["levels"] = cleaned_levels

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
        except OSError as error:
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
