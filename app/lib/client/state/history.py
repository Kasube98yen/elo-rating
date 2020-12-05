from tabulate import tabulate 
from collections import deque
from enum import Enum, auto
import discord

# 表出力用
import matplotlib.pyplot as plt
import japanize_matplotlib
import io
from PIL import ImageFont, ImageDraw, Image

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
            self.process = self.processmapper[0]
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
        with self.create_table(headers, res) as img:
            await message.channel.send(file=discord.File(img, "ranking.png"))
        return 0, True
    
    def create_table(self, headers:list, res:list):
        fig, ax = plt.subplots(figsize=(15,len(res)))
        ax.axis('off')
        ax.axis('tight')
        tb = ax.table(cellText=res, colLabels=headers, colWidths = [0.15, 0.50, 0.25], bbox=[0,0,1,1])
        
        tb.set_fontsize(18)
        tb[0, 0].set_facecolor('#719be8')
        tb[0, 1].set_facecolor('#719be8')
        tb[0, 2].set_facecolor('#719be8')
        for i in range(2,len(res),2):
            tb[i, 0].set_facecolor('#d3e0f8')
            tb[i, 1].set_facecolor('#d3e0f8')
            tb[i, 2].set_facecolor('#d3e0f8')
        tb[0, 0].set_text_props(color='w')
        tb[0, 1].set_text_props(color='w')
        tb[0, 2].set_text_props(color='w')

        plt.savefig("temp.png")
        return open("temp.png", mode="rb")


class HistoryEloRankingByJob(HistoryDefault):
    async def do_task(self, message, data:dict):     
        await message.channel.send("工事中です！")
        return 0, True 