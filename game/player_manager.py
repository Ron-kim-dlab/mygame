import uuid
import random

class PlayerManager:
    def __init__(self):
        self.players = {}  # { id: {"x": 0, "y": 0, "color": "#RRGGBB"} }
        self.available_colors = [
            "#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231",
            "#911eb4", "#46f0f0", "#f032e6", "#bcf60c", "#fabebe",
            "#008080", "#e6beff", "#9a6324", "#fffac8", "#800000"
        ]

    def add_player(self):
        if not self.available_colors:
            raise Exception("No colors left")

        player_id = str(uuid.uuid4())
        color = random.choice(self.available_colors)
        self.available_colors.remove(color)

        self.players[player_id] = {
            "x": 0,
            "y": 0,
            "color": color
        }

        return player_id

    def remove_player(self, player_id):
        if player_id in self.players:
            color = self.players[player_id]["color"]
            self.available_colors.append(color)
            del self.players[player_id]

    def move_player(self, player_id, dx, dy):
        if player_id in self.players:
            self.players[player_id]["x"] += dx
            self.players[player_id]["y"] += dy

    def get_players(self):
        return self.players

    def get_player(self, player_id):
        return self.players.get(player_id, None)
