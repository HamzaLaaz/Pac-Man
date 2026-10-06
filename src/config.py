import json
from pydantic import BaseModel, Field, ValidationError


class LevelConfig(BaseModel):
    width: int = Field(default=15, gt=0)
    height: int = Field(default=15, gt=0)


class GameSettings(BaseModel):
    max_time: int = Field(default=90, gt=0)
    first_level_seed: int = 42
    levels: list[LevelConfig] = Field(
        default_factory=lambda: [LevelConfig() for _ in range(10)],
        min_length=10,
    )


class PlayerConfig(BaseModel):
    lives: int = Field(default=3, gt=0)


class ScoreConfig(BaseModel):
    pacgum: int = Field(default=10, ge=0)
    super_pacgum: int = Field(default=50, ge=0)
    ghost: int = Field(default=200, ge=0)


class Config(BaseModel):
    highscore_filename: str = "highscores.json"
    game_settings: GameSettings = Field(default_factory=GameSettings)
    player: PlayerConfig = Field(default_factory=PlayerConfig)
    score: ScoreConfig = Field(default_factory=ScoreConfig)

    @classmethod
    def get_config(cls, filename: str) -> "Config":
        try:
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)
            return cls.model_validate(data)
        except FileNotFoundError:
            print(f"Warning: {filename} not found."
                  " Using default configuration.")
            return cls()

        except json.JSONDecodeError:
            print(f"Warning: {filename} contains invalid JSON."
                  " Using default configuration.")
            return cls()

        except ValidationError:
            print(f"Warning: {filename} contains invalid values."
                  " Using default configuration.")
            return cls()
