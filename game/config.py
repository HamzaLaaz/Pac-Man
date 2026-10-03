import json


DEFAULT_MAX_TIME = 90
DEFAULT_SEED = 42
DEFAULT_LIVES = 3
DEFAULT_PACGUM_SCORE = 10
DEFAULT_SUPER_PACGUM_SCORE = 50
DEFAULT_GHOST_SCORE = 200

class Config:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.data = self.load()
        game = self.data.get("game_settings", {})

        self.max_time = game.get("max_time", DEFAULT_MAX_TIME)
        self.first_level_seed = game.get("first_level_seed", DEFAULT_SEED)
        self.levels = game.get("levels", [])

        player = self.data.get("player", {})
        self.player_lives = player.get("lives", DEFAULT_LIVES)

        score = self.data.get("score", {})
        self.pacgum_score = score.get("pacgum", DEFAULT_PACGUM_SCORE)
        self.super_pacgum_score = score.get(
            "super_pacgum", DEFAULT_SUPER_PACGUM_SCORE)
        self.ghost_score = score.get("ghost", DEFAULT_GHOST_SCORE)

    def load(self) -> dict:
        with open(self.filename, "r", encoding="utf-8") as file:
            return json.load(file)
