import redis,configparser,os

class RedisDB():
    def __init__(self):
        config = configparser.ConfigParser()
        config.read(os.getcwd()+'/config.ini','utf-8')
        REDIS_HOST = config.get('redis','host')
        REDIS_PORT = config.get('redis','port')
        REDIS_AUTH = config.get('redis','auth')
        REDIS_NUM  = config.get('redis','num')
        
        self.host  = REDIS_HOST
        self.auth  = REDIS_AUTH
        self.dbnum = REDIS_NUM
        self.port  = REDIS_PORT
        pool = redis.ConnectionPool(host=self.host, db=self.dbnum, password=self.auth, port=self.port,decode_responses=True)  
        self.db = redis.Redis(connection_pool=pool)

    def getConnect(self):
        return self.db