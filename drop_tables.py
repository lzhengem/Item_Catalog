from sqlalchemy import create_engine
from models import Base, Category, Item, User
import os

# if it is production, then use the database url
# if it is not production, use psycopg2
if os.getenv('FLASK_ENV') == 'production':
    database_url = os.getenv('DATABASE_URL')
    engine = create_engine(database_url)
else:
    engine = create_engine('postgresql+psycopg2:///item_catalog')

Base.metadata.drop_all(bind=engine, tables=[Item.__table__,
                       User.__table__, Category.__table__])
