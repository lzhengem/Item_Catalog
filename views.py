from flask import Flask, jsonify, render_template, url_for, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Category, Item
import os

#for login
from flask import session as login_session, make_response
import random, string
import json

#imports for google login
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import FlowExchangeError #if running into error while exchanging authorization token for access token
import httplib2 #HTTP client library in python

app = Flask(__name__)
app.secret_key = 'super_secret_key'

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
@app.route("/catalog/<category_id>/items/")
def category_items(category_id):
    category = session.query(Category).filter_by(id=category_id).first()
    if category is None:
        return "There is no such category as %s!" % category_name
    items = session.query(Item).filter_by(cat_id=category.id)
    return render_template('items.html', category=category, items=items)

#specific item in the category
@app.route("/catalog/<category_id>/<item_id>/")
def item(category_id,item_id):
    category = session.query(Category).filter_by(id=category_id).first()
    item = session.query(Item).filter_by(id=item_id).first()
    if category is None:
        return "Category '%s' does not exist!" % category_id
    elif item is None:
        return "Item '%s' does not exist!" % item_id
    elif item.category != category:
        return "%s does not have an item '%s'" %(category_id, item_id)
    return render_template('item.html',category=category,item=item)

#edit the category
@app.route("/catalog/<item_id>/edit/", methods=["GET","POST"])
def edit(item_id):
    item = session.query(Item).filter_by(id=item_id).first()

    #if they are trying to update, check if they entered any data for title and description
    if request.method == "POST":
        title = request.form.get('title').strip()
        description = request.form.get('description')
        cat_id = request.form.get('cat_id')
    
        #only update if they changed one of the fields. avoids db hits
        if item.description != description or str(item.cat_id) != cat_id or item.title != title:

            #only update the title if they provided a title that is not empty
            if title:
                item.title = title        
            item.description = description
            item.cat_id = cat_id
            session.add(item)

            return "You have updated %s" % item.title
        else:
            return "You didnt change anything!"
    elif request.method == 'GET':
        if item:
            categories = session.query(Category).all()
            return render_template('edit.html',item=item,categories=categories)
        else:
            return "That item does not exist!"

#delete the category
@app.route("/catalog/<item_id>/delete/",methods=["GET","POST"])
def delete(item_id):
    item = session.query(Item).filter_by(id=item_id).first()

    #check if the item exists
    if item is not None:
        #if it is a post method, delete it from the database
        if request.method == "POST":
            session.delete(item)
            session.commit()
            return 'Item was deleted'
        #if it is a get method, show the button to confirm if user wants to delete item
        return render_template('delete.html',item=item)
    #if the item does not exist, let the user know 
    else:
        return "Item %s does not exist" %item_id


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

#allow users to log in
@app.route('/login/')
def showLogin():
    #create a random string state to prevent cross site forgery
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    #save state in session
    login_session['state'] = state
    return render_template('login.html',STATE=state)

@app.route('/gconnect', methods=["POST"])
def gconnect():
    state = request.args.get('state')
    #if the state is not the same, then this person is not the one who logged in our login page
    if state != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'),401)
        response.headers['Content-type'] = 'application/json'
        return response

    #if the state tokens match, then get the google one time use code
    code = request.data
    try:
        CLIENT_ID = os.environ.get('ITEM_CATALOG_GOOGLE_ID')
        # CLIENT_SECRET = os.environ.get('ITEM_CATALOG_GOOGLE_SECRET')
        #upgrade the authorization code into a credentials object
        # oauth_flow = flow_from_clientsecrets('client_secrets.json',scope='')
        oauth_flow = OAuth2WebServerFlow(client_id=CLIENT_ID,
                           client_secret=CLIENT_SECRET,
                           scope='',
                           redirect_uri='postmessage')
        credentials = oauth_flow.step2_exchange(code)
    #if unable to exchange authorization code for credentials, give error response
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'),401)
        return response
    #if able to trade for credentials, check if access_token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %access_token)
    h=httplib2.Http()
    #result contains our client id and the logged in user's info
    result = json.loads(h.request(url,'GET')[1])

    #if there is an error in the access token, then give error response
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')),500)
        response.headers['Content-type'] = 'application/json'
        return response

    #if ther were no issues with the state or exchanging for access token,
    #check to see if the access token's id matches the google user id
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID does not match given user ID"),401)
        response.headers['Content-type'] = 'application/json'
        return response

    #verify that the access token is valid for our app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's user ID doesn't match app's ID"),401)
        response.headers['Content-type'] = 'application/json'
        return response


    response = make_response(json.dumps('Successfully Connected user'),200)
    return response


if __name__ == '__main__':

    app.debug = debug
    port = int(os.environ.get('PORT',8000))
    app.run(host='0.0.0.0',port=port)