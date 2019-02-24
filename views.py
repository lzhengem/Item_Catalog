from flask import Flask, jsonify, render_template, url_for, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Category, Item
import html
import os

app = Flask(__name__)
# print(os.getenv('FLASK_ENV')) 
if os.getenv('FLASK_ENV') == 'development':
    debug = True
    engine = create_engine('postgresql+psycopg2:///item_catalog')
elif os.getenv('FLASK_ENV') == 'production':
    debug = False
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
@app.route("/catalog/<category_name>/items/")
def category_items(category_name):
    safe_category_name = html.escape(category_name)
    category = session.query(Category).filter_by(name=safe_category_name).first()
    if category is None:
        return "There is no such category as %s!" % category_name
    items = session.query(Item).filter_by(cat_id=category.id)
    return render_template('items.html', category=category, items=items)

#specific item in the category
@app.route("/catalog/<category_name>/<item_title>/")
def item(category_name,item_title):
    safe_category_name = html.escape(category_name)
    safe_item_title = html.escape(item_title)
    category = session.query(Category).filter_by(name=safe_category_name).first()
    item = session.query(Item).filter_by(title=safe_item_title).first()
    if category is None:
        return "Category '%s' does not exist!" % category_name
    elif item is None:
        return "Item '%s' does not exist!" % item_title
    elif item.category != category:
        return "%s does not have an item '%s'" %(category_name, item_title)
    return render_template('item.html',category=category,item=item)

#edit the category
@app.route("/catalog/<item_title>/edit", methods=["GET","POST"])
def edit(item_title):
    safe_item_title = html.escape(item_title)
    item = session.query(Item).filter_by(title=safe_item_title).first()

    #if they are trying to update, check if they entered any data for title and description
    if request.method == "POST":
        title = request.form.get('title').strip()
        description = request.form.get('description')
        cat_id = request.form.get('cat_id')
        #only update the title if they provided one
        if title:
            item.title = title
        item.description = description
        item.cat_id = cat_id
        session.add(item)

        return "You have updated %s" % item.title
    elif request.method == 'GET':
        if item:
            categories = session.query(Category).all()
            return render_template('edit.html',item=item,categories=categories)
        else:
            return "That item does not exist!"

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
            if session.query(Item).filter_by(title=title).first() is not None:
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
    app.debug = debug
    port = int(os.environ.get('PORT',8000))
    app.run(host='0.0.0.0',port=port)