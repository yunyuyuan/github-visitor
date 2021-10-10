from dbutils.pooled_db import PooledDB
import pymysql
import config

DB = PooledDB(creator=pymysql,
              maxusage=10,
              host=config.db_host,
              database=config.db_db,
              user=config.db_user,
              port=config.db_port,
              password=config.db_pwd
              )
