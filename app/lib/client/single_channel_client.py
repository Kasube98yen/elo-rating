import discord
from collections import deque

from .state.add import Add
from .state.register import Register
from .state.history import History

class PvPElo(discord.Client):    
    def __init__(self, __conn, __SCHEMA):
        super().__init__()

        # state作成
        self.register = Register(__conn, __SCHEMA)
        self.add = Add(__conn, __SCHEMA)
        self.history = History(__conn, __SCHEMA)
        self.request = None

        # 環境情報
        self.schema = __SCHEMA # 送るスキーマ名
        self.conn = __conn # psycopg2の接続情報

    async def on_ready(self):
        print("Run")

    async def on_message(self, message):
        # ユーザからのリクエスト受け取り→リクエスト存在時タスク実行
        if message.author != self.user:
            if message.content.startswith("!"):
                await self.get_request(message)
            if self.request:
                await self.request.do_task(message)

    async def get_request(self, message):
        if message.content == "!register":
            self.request = self.register
        elif message.content == "!add":
            self.request = self.add
        elif message.content == "!history":
            self.request = self.history
        elif message.content == "!reset":
            await self.request.do_task(message)
            self.request = None

    async def do_task(self, message):
        await self.request.do_task(message)

    



