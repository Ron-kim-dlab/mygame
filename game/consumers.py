import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .player_manager import PlayerManager

player_manager = PlayerManager()

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.player_id = player_manager.add_player()
        self.room_group_name = "game_room"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # 초기 상태 전송
        await self.send(text_data=json.dumps({
            "type": "init",
            "id": self.player_id,
            "players": player_manager.get_players()
        }))

        # 브로드캐스트 전체 상태
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "broadcast_state"
            }
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get("type") == "move":
            dx = data.get("dx", 0)
            dy = data.get("dy", 0)
            player_manager.move_player(self.player_id, dx, dy)
            
            # 임시 로그
            print(f"[MOVE] Player {self.player_id[:8]} moved by ({dx}, {dy})")

            # 전체 상태 브로드캐스트
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "broadcast_state"
                }
            )

    async def disconnect(self, close_code):
        player_manager.remove_player(self.player_id)

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # 브로드캐스트 전체 상태
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "broadcast_state"
            }
        )

    async def broadcast_state(self, event):
        await self.send(text_data=json.dumps({
            "type": "update",
            "players": player_manager.get_players()
        }))
