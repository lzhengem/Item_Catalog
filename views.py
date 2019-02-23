from flask import Flask, jsonify, render_template, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Category, Item

app = Flask(__name__)
engine = create_engine('postgresql+psycopg2:///item_catalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

#lists all the categories
@app.route("/")
@app.route("/catalog/")
def homepage():
    categories = session.query(Category).all()
    return render_template('homepage.html', categories=categories)

#a json output of all the categories
@app.route("/catalog.json")
def category_json():
    return "You are at the category json page!"

#added items in selected category
@app.route("/catalog/<category>/items/")
def category_items(category):
    return "You are viewing %s items!" % category

#specific item in the category
@app.route("/catalog/<category>/<item>/")
def item(category,item):
    return "You are viewing %s in %s!" % (item,category)

#edit the category
@app.route("/catalog/<item>/edit/")
def edit(item):
    return "You are viewing %s edit page!" % item

#delete the category
@app.route("/catalog/<item>/delete/")
def delete(item):
    return "You are viewing %s delete page!" % item

#create new item
@app.route("/catalog/item/", methods=["GET","POST"])
def new_item():
    return "You are making a new item!"




if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0',port=8000)