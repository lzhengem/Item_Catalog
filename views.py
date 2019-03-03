from flask import Flask, jsonify, render_template, url_for, request, redirect
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
import httplib2 #HTTP client library in python. use this one for its get method, which returns None if object is not found
import requests #Apache 2.0 licensed HTTP library written in python

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

def logged_in():
    return True if 'username' in login_session else False
#lists all the categories
@app.route("/")
@app.route("/catalog/")
def catalog():
    categories = session.query(Category).all()
    return render_template('catalog.html', categories=categories, logged_in=logged_in())

#a json output of all the categories
@app.route("/catalog.json")
def category_json():
    categories = session.query(Category).all()
    serialized_categories = []
    for category in categories:
        

        #get all the items in the category
        items = session.query(Item).filter_by(category=category).all()
        serialized_items = [item.serialize for item in items]

        #serialize the current category and add the serialized item to it
        current_category = category.serialize
        current_category.update({"items" : serialized_items})
        
        serialized_categories.append(current_category)


        # print(serialized_categories)
    serialized_categories = {"categories" : serialized_categories}
    response = make_response(jsonify(serialized_categories))
    response.headers['Content-type'] = 'application/json'
    return response

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
    return render_template('item.html',category=category,item=item,logged_in=logged_in())

#edit the category
@app.route("/catalog/<item_id>/edit/", methods=["GET","POST"])
def edit(item_id):
    item = session.query(Item).filter_by(id=item_id).first()
    #if they are trying to update, check if they entered any data for title and description
    if logged_in() and request.method == "POST":
        title = request.form.get('title').strip()
        description = request.form.get('description')
        cat_id = request.form.get('cat_id')
    
        #only update if they changed one of the fields. avoids db hits
        if item and (item.description != description or str(item.cat_id) != cat_id or item.title != title):

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
            return render_template('edit.html',item=item,categories=categories, logged_in=logged_in())
        else:
            return "That item does not exist!"
    else:
        return render_template('edit.html',item=None,categories=None, logged_in=logged_in())

#delete the category
@app.route("/catalog/<item_id>/delete/",methods=["GET","POST"])
def delete(item_id):
    if logged_in():
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
    else:
        return 'Unauthorized Access'


#create new item
@app.route("/catalog/new/", methods=["GET","POST"])
def new():

    if logged_in() and request.method == 'POST':
        
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
    else:
        categories = session.query(Category).all() if logged_in() else None
        return render_template('new.html',categories=categories, logged_in=logged_in())

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
        CLIENT_SECRET = os.environ.get('ITEM_CATALOG_GOOGLE_SECRET')
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
    result = json.loads(h.request(url, 'GET')[1].decode())

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

    #check to see if user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    #if these 2 are stored and matches, then the user is already logged in
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('User is already connected'),200)
        response.headers['Content-type'] = 'application/json'
        return response

    #if access token user matches logged in user and client id matches our client id, get the user info from google
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    #store the users info in login_session
    login_session['provider'] = 'google'
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']


    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    return output

@app.route('/gdisconnect/')
def gdisconnect():
    #only disconnect a connected user
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user is not connected'),401)
        response.headers['Content-type'] = 'application/json'
        return response

    #if the user is connected, get the access token and revoke it
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    #if revoking was successful, reset the user's sessions and send user a 200 response
    del login_session['gplus_id']
    del login_session['access_token']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['provider']

    return redirect(url_for('catalog'))  

if __name__ == '__main__':

    app.debug = debug
    port = int(os.environ.get('PORT',8000))
    app.run(host='0.0.0.0',port=port)