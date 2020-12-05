import itertools
from collections import deque
from statistics import mean

from .default.processdefault import ProcessDefault
from .default.statedefault import StateDefault

class Add(StateDefault):
    def __init__(self, __conn, __SCHEMA):
        super().__init__(__conn, __SCHEMA)
           
        # state
        self.add_askteam1 = AddAskTeam1(__conn, __SCHEMA)
        self.add_inputteam1 = AddInputTeam1(__conn, __SCHEMA)
        self.add_askteam2 = AddAskTeam2(__conn, __SCHEMA)
        self.add_inputteam2 = AddInputTeam2(__conn, __SCHEMA)
        self.add_askwin = AddAskWin(__conn, __SCHEMA)
        self.add_inputwin = AddInputWin(__conn, __SCHEMA)
        self.add_sendquery = AddSendQuery(__conn, __SCHEMA)
        self.add_updateelo = AddUpdateElo(__conn, __SCHEMA)
        self.transition, self.transition_reset = itertools.tee(itertools.cycle([self.add_askteam1, self.add_inputteam1, self.add_askteam2, self.add_inputteam2, 
                                self.add_askwin, self.add_inputwin, self.add_sendquery, self.add_updateelo]))
        self.process = next(self.transition)


        # データ保存
        self.data = {"msgs": None, "team1": None, "team2": None, "win": None}    

    async def do_task(self, message):
        self.data["msgs"] = deque([line for line in message.content.split("\n") if line])
        continue_trigger = True
        
        if message.content == "!reset":
            self.reset_process()
            return 
        while continue_trigger:
            if not message.content.startswith("!"):
                self.process = next(self.transition)
            try:
                self.data, continue_trigger = await self.process.do_task(message, self.data)
            except ValueError:
                self.reset_process()

    def reset_process(self):
        self.transition = self.transition_reset
        self.process = next(self.transition)

class AddDefault(ProcessDefault):
    async def is_valid_teamdata(self, message, team):
        if len(team) != 3:
            await message.channel.send("入力形式に誤りがあります。もう一度入力してください。")
            raise ValueError("入力形式に誤りがあります")
            return False
        for member in team:
            if not self.send_query("lib/query/register/in_user_table.sql", [member], True): 
                await message.channel.send("メンバーが登録されていません。先にメンバーを登録してください。")
                raise ValueError("メンバーが登録されていません")
                return False
        return True

    async def is_valid_winteam(self, message, win):
        if win not in {"1", "2"}:
            await message.channel.send("入力形式に誤りがあります。もう一度入力してください。")
            raise ValueError("入力形式に誤りがあります")
            return False
        return True
    
class AddAskTeam1(AddDefault):
    async def do_task(self, message, data:dict):
        if len(data["msgs"]) == 0 or data["msgs"][0].startswith("!"):
            await message.channel.send("Add: TEAM1のメンバーを入力してください\n例: AAAA BBBB CCCC\n最初から入力する場合は`!reset`を入力してください")
        return data, len(data["msgs"]) > 0 and not data["msgs"][0].startswith("!")

class AddAskTeam2(AddDefault):
    async def do_task(self, message, data:dict):
        if len(data["msgs"]) == 0 or data["msgs"][0].startswith("!"):
            await message.channel.send("Add: TEAM2のメンバーを入力してください\n例:DDDD EEEE FFFF\n最初から入力する場合は`!reset`を入力してください")
        return data, len(data["msgs"]) > 0 and not data["msgs"][0].startswith("!")

class AddAskWin(AddDefault):
    async def do_task(self, message, data:dict):
        if len(data["msgs"]) == 0 or data["msgs"][0].startswith("!"):
            await message.channel.send("Add: 勝利したのは？(1 or 2)\n最初から入力する場合は`!reset`を入力してください")
        return data, len(data["msgs"]) > 0 and not data["msgs"][0].startswith("!")

class AddInputTeam1(AddDefault):
    async def do_task(self, message, data:dict):
        team = data["msgs"].popleft().split()
        if await self.is_valid_teamdata(message, team):
            data["team1"] = team
            return data, True

class AddInputTeam2(AddDefault):
    async def do_task(self, message, data:dict):
        team = data["msgs"].popleft().split()
        if await self.is_valid_teamdata(message, team):
            data["team2"] = team
            return data, True

class AddInputWin(AddDefault):
    async def do_task(self, message, data:dict):
        win = data["msgs"].popleft()
        if await self.is_valid_winteam(message, win):
            data["win"] = win
            return data, True

class AddSendQuery(AddDefault):
    async def do_task(self, message, data:dict):
        for user in data["team1"]:
            self.send_query("lib/query/add/add_battles_teamside.sql", [user, 1], False)
        for user in data["team2"]:
            self.send_query("lib/query/add/add_battles_teamside.sql", [user, 2], False)
        self.send_query("lib/query/add/add_result.sql",[data["win"]],False)    
        return data, True

class AddUpdateElo(AddDefault):
    async def do_task(self, message, data:dict):
        elo_team1, elo_team2 = {}, {}
        for user in data["team1"]:
            res = self.send_query("lib/query/add/get_elo.sql", [user], True)
            elo_team1[user] = float(res[0][0]) if res else 1500
        for user in data["team2"]:
            res = self.send_query("lib/query/add/get_elo.sql", [user], True)
            elo_team2[user] = float(res[0][0]) if res else 1500

        new_elo_team1, new_elo_team2 = self.calc_elo(elo_team1, elo_team2, data["win"])

        for user, newelo in new_elo_team1.items():
            self.send_query("lib/query/add/send_elo.sql",[user, newelo], False)
        for user, newelo in new_elo_team2.items():
            self.send_query("lib/query/add/send_elo.sql",[user, newelo], False)
    
        await message.channel.send("TEAM1: {} {} {}\nTEAM2: {} {} {}\n勝利: TEAM{} で登録しました".format(*(data["team1"] + data["team2"] + [data["win"]])))              

        return data, True

    def calc_elo(self, elo_team1:dict, elo_team2:dict, which_was_won:int, K=32):
        E1, E2 = {}, {}
        newR1, newR2 = {}, {}

        # チーム平均レートを計算
        TeamR1 = mean(elo_team1.values()) 
        TeamR2 = mean(elo_team2.values())

        # 勝率算出
        for user, elo in elo_team1.items():
            E1[user] = 1 / (1 + pow(10, (TeamR2-elo)/400))
        for user, elo in elo_team2.items():
            E2[user] = 1 / (1 + pow(10, (TeamR1-elo)/400))

        # 勝敗結果を反映したelo算出
        win_corrected = 1 if which_was_won == 1 else 0

        for user in elo_team1.keys():
            newR1[user] = elo_team1[user] + K * (win_corrected - E1[user])
        for user in elo_team2.keys():
            newR2[user] = elo_team2[user] + K * ((1 - win_corrected) - E2[user])
        
        return newR1, newR2   
