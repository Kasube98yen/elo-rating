from tabulate import tabulate 
from collections import deque
from enum import Enum, auto

# 表出力用
import matplotlib.pyplot as plt

from .default.processdefault import ProcessDefault
from .default.statedefault import StateDefault

class History(StateDefault):
    def __init__(self, __conn, __SCHEMA):
        super().__init__(__conn, __SCHEMA,)
           
        # state作成
        self.history_start = HistoryStart(__conn, __SCHEMA)
        self.history_latestplay = HistoryLatestPlay(__conn, __SCHEMA)
        self.history_individualdata = HistoryIndividualData(__conn, __SCHEMA)
        self.history_eloranking = HistoryEloRanking(__conn, __SCHEMA)
        self.history_eloranking_byjob = HistoryEloRankingByJob(__conn, __SCHEMA)
        

        self.processmapper = [self.history_start, self.history_latestplay, self.history_individualdata, 
                              self.history_eloranking, self.history_eloranking_byjob]
        self.process = self.processmapper[0]
        
        self.data = {}

    async def do_task(self, message):
        self.data["msgs"] = deque([line for line in message.content.split("\n") if line])
        continue_trigger = True

        if message.content == "!reset":
            self.process = None
            return 
        if self.data["msgs"][0].startswith("!"):
            selector = 0
        else:
            try:
                selector = int(self.data["msgs"].popleft())
            except ValueError:
                return
        while continue_trigger:
            self.process = self.processmapper[selector]
            if self.process == self.history_start:
                _, continue_trigger = await self.process.do_task(message, self.data)
            else:
                selector, continue_trigger = await self.process.do_task(message, self.data)

class HistoryDefault(ProcessDefault):
    pass

class HistoryStart(HistoryDefault):
    async def do_task(self, message, data:dict):     
        await message.channel.send("History: 数字を入力してください\n1. 直近の試合結果 2. 個人成績 3. レートランキング 4. 職別レートランキング \n終了する場合は`!reset`")
        return 0, False

class HistoryLatestPlay(HistoryDefault):
    async def do_task(self, message, data:dict):     
        await message.channel.send("工事中です！") 
        return 0, True 

class HistoryIndividualData(HistoryDefault):
    async def do_task(self, message, data:dict):     
        await message.channel.send("工事中です！") 
        return 0, True 

class HistoryEloRanking(HistoryDefault):
    async def do_task(self, message, data:dict):
        res = self.send_query("lib/query/history/get_eloranking.sql",[],True)
        headers = ["ランキング", "ユーザー名", "レート"]
        await message.channel.send("```" + tabulate(res,headers,tablefmt="psql") + "```")
        print(tabulate(res,headers,tablefmt="psql"))
        return 0, True

class HistoryEloRankingByJob(HistoryDefault):
    async def do_task(self, message, data:dict):     
        await message.channel.send("工事中です！")
        return 0, True 