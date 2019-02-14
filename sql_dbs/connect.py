from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


USER = 'root'
PASSWORD = 'qwe123'
HOST = '127.0.0.1'
PORT = '3306'
DATABASE = 'userdb'

db_url = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(
    USER,
    PASSWORD,
    HOST,
    PORT,
    DATABASE
)

engine = create_engine(db_url)
Base = declarative_base(engine)
Session = sessionmaker(engine)
session = Session()


if __name__ == '__main__':
    cursor = engine.connect()
    result = cursor.execute('select 1')
    print(result.fetchone())
