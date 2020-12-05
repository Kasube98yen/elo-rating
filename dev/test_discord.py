# TODO: Stateパターンに寄せる

import discord
import psycopg2
from statistics import mean
from enum import Flag, auto

class RequestState(Flag):
    REGISTER = auto()
    ADD = auto()
    history = auto()

class RegisterState(Flag):
    ASKED = auto()

class AddState(Flag):
    TEAM1_ASKED = auto()
    TEAM1_INPUTTED = auto()
    TEAM2_ASKED = auto()
    TEAM2_INPUTTED = auto()
    TEAM_CHECKED = auto()
    WIN_ASKED = auto()

class HistoryState(Flag):
    ASKED = auto()
    INDIVIDUAL_REQUESTED = auto()
    OVERALL_REQUESTED = auto()
    JOBALL_REQUESTED = auto()

class PvPCalc(discord.Client):

    def __init__(self, __DNS_INFO, __env):
        super().__init__()
        self.request = None
        self.process_status = None
        self.input_request = True
        self.env = __env

        conn = psycopg2.connect(__DNS_INFO)
        self.cur = conn.cursor()

    async def on_ready(self):
        print("Run")

    async def on_message(self, message):
        # ユーザからのリクエスト受け取り→リクエスト存在時タスク実行
        if message.author != self.user:
            self.input_request = False
            if message.content.startswith("!"):
                self.get_status(message)
            while self.request and not self.input_request:
                await self.do_task(message)

    def get_status(self, message):
        if message.content == "!register":
            self.request = RequestState.REGISTER
        elif message.content == "!add":
            self.request = RequestState.ADD
        elif message.content == "!history":
            self.request = RequestState.history
        elif message.content == "!exit":
            self.process_status = None
            self.request = None
            self.input_request = True
        else:
            self.request = None
            self.input_request = True

    async def do_task(self, message):
        # !registerの実施
        if self.request == RequestState.REGISTER:
            await self.register_player(message)
        # !addの実施
        elif self.request == RequestState.ADD:
            await self.add_result(message)
        # !historyの実施
        elif self.request == RequestState.history:
            await self.show_history(message)

    async def register_player(self, message):
        if self.process_status is None:
            await message.channel.send("Register: キャラ名と職を入力してください (例:Pigepic6SV ウォーロード)\n 終了する場合は!exit")
            self.process_status = RegisterState.ASKED
            self.input_request = True
        elif self.process_status == RegisterState.ASKED:
            userdata = message.content.split()
            if await self.is_valid_userdata(userdata, message):
                self.send_query("../lib/query/register/register_player.sql", userdata, False)
                player_name, job = userdata
                await message.channel.send("プレイヤー名: {}, 職名: {} で登録しました".format(player_name, job))
                self.process_status, self.request = None, RequestState.REGISTER
            else:
                self.process_status, self.request = None, RequestState.REGISTER
            self.input_request = False

    async def add_result(self, message):
        if self.process_status is None:
            await message.channel.send("Add: TEAM1のメンバーを入力してください (例:AAAA BBBB CCCC)")
            self.process_status = AddState.TEAM1_ASKED

        elif self.process_status == AddState.TEAM1_ASKED:
            self.team1 = message.content.split()
            await message.channel.send("Add: TEAM2のメンバーを入力してください (例:DDDD EEEE FFFF)")
            self.process_status = AddState.TEAM2_ASKED
 
        elif self.process_status == AddState.TEAM2_ASKED:
            self.team2 = message.content.split()
            if await self.is_valid_teamdata(self.team1, self.team2, message):
                # 事前ELO表示機能見合わせ中
                # elo = {}
                # msg = "TEAM1\n"
                # for user in TEAM1:
                #     res = self.send_query("lib/query/add/get_elo.sql", [user], True)
                #     elo[user] = res[0][0]
                #     msg += "{}: {}\n".format([user,elo[user]])
                # msg += "TEAM2\n"
                # for user in TEAM2:
                #     res = self.send_query("lib/query/add/get_elo.sql", [user], True)
                #     elo[user] = res[0][0]
                #     msg += "{}: {}\n".format([user,elo[user]])
                # await message.channel.send(msg + "このチーム構成でいいですか？(Y or N)")
                self.process_status = AddState.TEAM_CHECKED
                return # 機能実装見合わせ中
            else:
                await message.channel.send("Add: TEAM1のメンバーを入力してください (例:AAAA BBBB CCCC)")
                self.process_status = AddState.TEAM1_ASKED
            
        elif self.process_status == AddState.TEAM_CHECKED:
            await message.channel.send("勝利したのは？(1 or 2)")
            self.process_status = AddState.WIN_ASKED

            # 機能実装見合わせ中
            # if message.content in {"Y","y"} :
            #     await message.channel.send("勝利したのは？(1 or 2)")
            #     self.process_status = AddState.WIN_ASKED
            # else:
            #     self.process_status = None

        elif self.process_status == AddState.WIN_ASKED:
            win = message.content
            if await self.is_valid_winteam(win, message):
                self.send_query("../lib/query/add/add_result.sql",[win],False)
                for user in self.team1:
                    self.send_query("../lib/query/add/add_battles_teamside.sql", [user, 1], False)
                for user in self.team2:
                    self.send_query("../lib/query/add/add_battles_teamside.sql", [user, 2], False)                    
                await message.channel.send("TEAM1: {}, {}, {}\nTEAM2: {}, {}, {}\n勝利: TEAM{} で登録しました".format(*(self.team1 + self.team2 + [win])))
                
                elo_team1, elo_team2 = {}, {}
                msg = "TEAM1\n"
                for user in self.team1:
                    res = self.send_query("../lib/query/add/get_elo.sql", [user], True)
                    elo_team1[user] = float(res[0][0]) if res else 1500
                for user in self.team2:
                    res = self.send_query("../lib/query/add/get_elo.sql", [user], True)
                    elo_team2[user] = float(res[0][0]) if res else 1500

                new_elo_team1, new_elo_team2 = self.calc_elo(elo_team1, elo_team2, win)

                for user, newelo in new_elo_team1.items():
                    self.send_query("../lib/query/add/send_elo.sql",[user, newelo], False)
                for user, newelo in new_elo_team2.items():
                    self.send_query("../lib/query/add/send_elo.sql",[user, newelo], False)
                self.process_status, self.request = None, None
        self.input_request = True

    async def show_history(self, message):
        history_mapper = {"1":HistoryState.INDIVIDUAL_REQUESTED, "2":HistoryState.OVERALL_REQUESTED, "3":HistoryState.JOBALL_REQUESTED}
        if self.process_status is None:
            await message.channel.send("Histroy: 数字を入力してください。1.個人スコア 2.全体ランキング 3.職別ランキング")
            self.process_status = HistoryState.ASKED
        
        elif self.process_status == HistoryState.ASKED:
            if self.is_valid_history_request(message):
                self.process_status = history_mapper[message.content]

        elif self.process_status == HistoryState.INDIVIDUAL_REQUESTED:
            await message.channel.send("工事中です！")
            self.process_status, self.request = None, None
        elif self.process_status == HistoryState.OVERALL_REQUESTED:
            await message.channel.send("工事中です！")
            self.process_status, self.request = None, None
        elif self.process_status == HistoryState.JOBALL_REQUESTED:
            await message.channel.send("工事中です！")
            self.process_status, self.request = None, None


    async def is_valid_userdata(self, userdata, message):
        if len(userdata) != 2:
            await message.channel.send("入力形式に誤りがあります。もう一度入力してください。")
            return False

        player_name, job = userdata

        if not self.send_query("../lib/query/register/in_job_table.sql", [job], True):
            await message.channel.send("職の名前が正しくありません。もう一度入力してください。")
            return False
        if self.send_query("../lib/query/register/in_user_table.sql", [player_name], True): 
            await message.channel.send("既に登録済みです。または、類似の名前が登録されています。")
            self.process_status, self.request = None, None
            return False
        return True
    
    async def is_valid_teamdata(self, team1, team, message):
        if len(team1) != 3 or len(team1) != 3:
            await message.channel.send("入力形式に誤りがあります。もう一度入力してください。")
            return False
        for member in self.team1 + self.team2:
            if not self.send_query("../lib/query/register/in_user_table.sql", [member], True): 
                await message.channel.send("メンバーが登録されていません。先にメンバーを登録してください。ゲスト扱いの場合はguest1, guest2, ...の形で入力してください。")
                self.process_status, self.request = None, None
                return False
        return True
    
    async def is_valid_winteam(self, win, message):
        if win not in {"1", "2"}:
            await message.channel.send("入力形式に誤りがあります。もう一度入力してください。")
            return False
        return True

    async def is_valid_history_request(self, message):
        if message.content not in {"1","2","3"}:
            await message.channel.send("入力が不正です")
            self.process_status = None
            return False
        else:
            return True

    def send_query(self, queryfile:str, params:list, selectflag:bool):
        res = None
    
        with open(queryfile) as f:
            query = f.read()
            print(query.format([self.env] + params))
            self.cur.execute(query.format([self.env] + params))
            if selectflag:
                res = self.cur.fetchall()
                print(res)
        return res

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
        



TOKEN = "********"
DNS_INFO = "host=******** port=****** dbname=****** user=****** password=********"
SCHEMA = "develop"

client = PvPCalc(DNS_INFO, env)

client.run(TOKEN)