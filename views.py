from flask import Flask, jsonify, render_template, url_for, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Category, Item
import os

app = Flask(__name__)
# print(os.getenv('FLASK_ENV')) 
if os.getenv('FLASK_ENV') == 'development':
    engine = create_engine('postgresql+psycopg2:///item_catalog')
elif os.getenv('FLASK_ENV') == 'production':
    database_url = os.getenv('DATABASE_URL')
    engine = create_engine(database_url)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

#lists all the categories
@app.route("/")
@app.route("/catalog/")
def catalog():
    categories = session.query(Category).all()
    return render_template('catalog.html', categories=categories)

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
@app.route("/catalog/new/", methods=["GET","POST"])
def new():
    if request.method == 'POST':
        #check to see if they entered a title
        if request.form.get('title'):
            title = request.form.get('title')
            if session.query(Item).one() is not None:
                return "That item exists already"

            cat_id = request.form.get('category')
            description = request.form.get('description')
            item = Item(cat_id=cat_id,title=title,description=description)
            session.add(item)
            session.commit()
            return "You have added a new item! category id: %s , title: %s, description: %s" % (cat_id,title,description)
    categories = session.query(Category).all()
    return render_template('new.html',categories=categories)




if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0',port=8000)