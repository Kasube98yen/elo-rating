import itertools
from collections import deque

from .default.processdefault import ProcessDefault
from .default.statedefault import StateDefault

class Register(StateDefault):
    def __init__(self, __conn, __SCHEMA):
        super().__init__(__conn, __SCHEMA,)
           
        # state作成
        self.register_start = RegisterStart(__conn, __SCHEMA)
        self.register_ongoing = RegisterOngoing(__conn, __SCHEMA)
        self.transition, self.transition_reset = itertools.tee(itertools.cycle([self.register_start, self.register_ongoing]))
        self.process = next(self.transition)

        self.data = {"msgs": None, }

    async def do_task(self, message):
        self.data["msgs"] = deque([line for line in message.content.split("\n") if line])
        continue_trigger = True
        
        if message.content == "!reset":
            self.transition = self.transition_reset
            self.process = next(self.transition)
            return 
        while continue_trigger:
            if not message.content.startswith("!"):
                self.process = next(self.transition)
            try:
                self.data, continue_trigger = await self.process.do_task(message, self.data)
            except ValueError:
                self.process = None
                self.transition = self.transition_reset
    
    def reset_process(self):
        self.transition = self.transition_reset
        self.process = next(self.transition)

class RegisterDefault(ProcessDefault):
    async def is_valid_userdata(self, userdata, message):
        if len(userdata) != 2:
            await message.channel.send("入力形式に誤りがあります。もう一度入力してください。")
            raise ValueError("入力形式に誤りがあります")
            return False
        player_name, job = userdata

        if not self.send_query("lib/query/register/in_job_table.sql", [job], True):
            await message.channel.send("職の名前が正しくありません。もう一度入力してください。")
            raise ValueError("職の名前が正しくありません")
            return False
        if self.send_query("lib/query/register/in_user_table.sql", [player_name], True): 
            await message.channel.send("既に登録済みです。または、類似の名前が登録されています。")
            raise ValueError("既に登録済みです")
            return False
        return True  

class RegisterStart(RegisterDefault):  
    async def do_task(self, message, data:dict):     
        if len(data["msgs"]) == 0 or data["msgs"][0].startswith("!"):
            await message.channel.send("Register: キャラ名と職を入力してください\n例:Pigepic6SV ウォーロード\n終了する場合は`!reset`")
        # 入力がコマンドであった場合、最初の要求で停止したい 
        return data, len(data["msgs"]) > 0 and not data["msgs"][0].startswith("!")
        
class RegisterOngoing(RegisterDefault):
    async def do_task(self, message, data:dict):
        userdata = data["msgs"].popleft().split()
        if await self.is_valid_userdata(userdata, message):
            self.send_query("lib/query/register/register_player.sql", userdata, False)
            player_name, job = userdata
            await message.channel.send("プレイヤー名: {}, 職名: {} で登録しました".format(player_name, job))
        return data, True