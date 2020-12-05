

class ProcessDefault():
    def __init__(self, __conn, __SCHEMA):
        # 環境情報
        self.schema = __SCHEMA # 送るスキーマ名
        self.conn = __conn # psycopg2の接続情報
    
    def send_query(self, querypath:str, params:list, selectflag:bool):
        res = None
        
        with self.conn.cursor() as cur, open(querypath,encoding="utf-8") as f:
            query = f.read()
            print("QUERY:\n" + query.format([self.schema] + params))
            cur.execute(query.format([self.schema] + params))
            if selectflag:
                res = cur.fetchall()
                print("RESULT:")
                print(res)
            self.conn.commit()
        return res
        
    async def do_task(self, message, data:dict):
        return data, True