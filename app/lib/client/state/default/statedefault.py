

class StateDefault():
    def __init__(self, __conn, __SCHEMA):
        # 環境情報
        self.schema = __SCHEMA # 送るスキーマ名
        self.conn = __conn # psycopg2の接続情報 
    
    async def do_task(self, message):
        pass
