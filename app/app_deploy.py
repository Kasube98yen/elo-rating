from lib.client.single_channel_client import PvPElo
import psycopg2
import discord

TOKEN = "********"
DNS_INFO = "host=******** port=****** dbname=****** user=****** password=********"
SCHEMA = "deploy"



conn = psycopg2.connect(DNS_INFO)
client = PvPElo(conn, SCHEMA)

client.run(TOKEN)