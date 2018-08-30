import os
import sqlalchemy

#импортируем классы таблиц
from db.alchemy import Company

class Connect:
    def __init__(self):
        #создадим подключение к базе
        path = os.path.join('db', 'counter.db')
        engine = sqlalchemy.create_engine('sqlite:///{}'.format(path))
        #создадим сессию для базы
        self.session = sqlalchemy.orm.sessionmaker(bind=engine)()
    
    def get_session(self):
        return self.session