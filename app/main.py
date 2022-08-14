import bot
import create_db
from create_db import engine

if __name__ == '__main__':
    create_db.create_tables(engine)
    create_db.get_session(engine)
    bot.start()

