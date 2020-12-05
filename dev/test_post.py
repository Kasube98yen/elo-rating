import psycopg2

def send_query(DNS_INFO:str, queryfile:str, params:list, selectflag:bool):
    with psycopg2.connect(DNS_INFO) as conn:
        with conn.cursor() as cur, open(queryfile, encoding="utf-8") as f:
            query = f.read()
            print(query.format(params))
            cur.execute(query.format(params))
            if selectflag:
                results = cur.fetchall()
                return results


TOKEN = "********"
DNS_INFO = "host=******** port=****** dbname=****** user=****** password=********"
SCHEMA = "develop"

# queryfile = "lib/query/register_player.sql"
# params = ['develop', 'satou', 'ランスマスター']
# queryfile = "lib/query/init_add_job.sql"
# params = 'develop'
queryfile = "lib/query/register/register_player.sql"
params = ['develop', "PigePic6SV", "ウォーロード"]

result = send_query(DNS_INFO, queryfile, params, False)

print(result)