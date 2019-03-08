from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Category, Item
import os

# if it is production, then use the database url
# if it is not production, use psycopg2
if os.getenv('FLASK_ENV') == 'production':
    database_url = os.getenv('DATABASE_URL')
    engine = create_engine(database_url)
else:
    engine = create_engine('postgresql+psycopg2:///item_catalog')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

Soccer = Category(name='Soccer')
Basketball = Category(name='Basketball')
Baseball = Category(name='Baseball')
Frisbee = Category(name='Frisbee')
Snowboarding = Category(name='Snowboarding')
Rock_Climbing = Category(name='Rock Climbing')
Foosball = Category(name='Foosball')
Skating = Category(name='Skating')
Hockey = Category(name='Hockey')

session.add(Soccer)
session.add(Basketball)
session.add(Baseball)
session.add(Frisbee)
session.add(Snowboarding)
session.add(Rock_Climbing)
session.add(Foosball)
session.add(Skating)
session.add(Hockey)

session.commit()
