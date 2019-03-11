from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import os
# to create a database if they dont have one yet
from sqlalchemy_utils import database_exists, create_database

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(80), unique=True, nullable=False)


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True, nullable=False)

    @property
    def serialize(self):
        return {'id': self.id,
                'name': self.name}


class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String)
    cat_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {'cat_id': self.cat_id,
                'description': self.description,
                'id': self.id,
                'title': self.title,
                'user_id': self.user_id}


if os.getenv('FLASK_ENV') == 'production':
    database_url = os.getenv('DATABASE_URL')
    engine = create_engine(database_url)
else:
    engine = create_engine('postgresql+psycopg2:///item_catalog')
# if item_catalog does not exist yet, then create it
if not database_exists(engine.url):
    create_database(engine.url)
Base.metadata.create_all(engine)
