import json
from channels.generic.websocket import AsyncWebsocketConsumer

# 전역 관리 (임시 메모리 – 실제로는 redis나 DB로 이전 가능)
connected_users = {}  # channel_name -> user info
available_colors = [
    "#FF5733", "#33FF57", "#3357FF", "#F39C12",
    "#9B59B6", "#1ABC9C", "#E74C3C", "#2ECC71"
]

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not available_colors:
            await self.close()  # 색상 다 떨어졌으면 접속 불가
            return

        # 유저 고유 색상 및 초기 좌표 부여
        color = available_colors.pop(0)
        connected_users[self.channel_name] = {
            'color': color,
            'x': 0,
            'y': 0,
        }

        await self.accept()

        # 전체 사용자 목록 브로드캐스트
        await self.broadcast_users()

    async def disconnect(self, close_code):
        user = connected_users.pop(self.channel_name, None)
        if user:
            available_colors.append(user['color'])  # 색상 반환

        await self.broadcast_users()

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'move':
            dx, dy = data['dx'], data['dy']
            if self.channel_name in connected_users:
                connected_users[self.channel_name]['x'] += dx
                connected_users[self.channel_name]['y'] += dy

        await self.broadcast_users()

    async def broadcast_users(self):
        users = [
            {
                'id': ch,
                'color': info['color'],
                'x': info['x'],
                'y': info['y']
            }
            for ch, info in connected_users.items()
        ]
        message = {
            'type': 'users_update',
            'users': users
        }
        for ch in connected_users.keys():
            await self.channel_layer.send(ch, {
                'type': 'send_update',
                'message': message
            })

    async def send_update(self, event):
        await self.send(text_data=json.dumps(event['message']))
