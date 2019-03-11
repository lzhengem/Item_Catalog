from flask import Flask, jsonify, render_template, url_for, request, redirect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Category, Item, User
# import for catching sqlalchemy exceptions
from sqlalchemy import exc
import os

# for login
from flask import session as login_session, make_response
import random
import string
import json

# imports for google login
from oauth2client.client import OAuth2WebServerFlow
# catch errors while exchanging authorization token for access token
from oauth2client.client import FlowExchangeError
# HTTP client library. get method returns None if object is not found
import httplib2
# Apache 2.0 licensed HTTP library written in python
import requests

# imports for flash messages
from flask import flash
app = Flask(__name__)
app.secret_key = 'super_secret_key'


# if in production(Heroku) then use their database url
# else it is development, use the postgres engine
if os.getenv('FLASK_ENV') == 'production':
    debug = False
    database_url = os.getenv('DATABASE_URL')
    engine = create_engine(database_url)
else:
    debug = True
    engine = create_engine('postgresql+psycopg2:///item_catalog')

# bind the engine
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def logged_in():
    """check to see if user is logged in"""
    return True if 'username' in login_session else False


@app.route("/")
@app.route("/catalog/")
def catalog():
    """lists all the categories"""
    categories = session.query(Category).all()
    return render_template('catalog.html', categories=categories,
                           logged_in=logged_in())


@app.route("/catalog/<category_id>/items/")
def category_items(category_id):
    """show the category and its items"""
    category = session.query(Category).filter_by(id=category_id).first()

    # if the category does not exist, flash an error message
    if category is None:
        flash("There is no such category as %s!" % category_name)
        return redirect(url_for('catalog'))
    items = session.query(Item).filter_by(cat_id=category.id)
    return render_template('items.html', category=category, items=items,
                           logged_in=logged_in())


@app.route("/catalog/<category_id>/<item_id>/")
def item(category_id, item_id):
    """specific item in the category"""
    category = session.query(Category).filter_by(id=category_id).first()
    item = session.query(Item).filter_by(id=item_id).first()
    owner = getUserInfo(item.user_id)
    # check to see if the edit and delete link should be shown to this user
    show_update_links = False
    if logged_in():
        user_id = getUserID(login_session['email'])
        if item.user_id == user_id:
            show_update_links = True

    # if theres no category or item, then flash error message
    if category is None:
        flash("Category '%s' does not exist!" % category_id)
        return redirect(url_for('catalog'))
    elif item is None:
        flask("Item '%s' does not exist!" % item_id)
        return redirect(url_for('catalog'))
    elif item.category != category:
        flask("%s does not have an item '%s'" % (category_id, item_id))
        return redirect(url_for('catalog'))
    return render_template('item.html', category=category, item=item,
                           owner=owner, show_update_links=show_update_links,
                           logged_in=logged_in())


@app.route("/catalog.json")
def catalog_json():
    """json output of all the categories along with its items"""
    categories = session.query(Category).all()
    serialized_categories = []
    for category in categories:

        # get all the items in the category
        items = session.query(Item).filter_by(category=category).all()
        serialized_items = [item.serialize for item in items]

        # serialize the current category and add its serialized items to it
        current_category = category.serialize
        current_category.update({"items": serialized_items})
        serialized_categories.append(current_category)

    # output the categories and its items
    serialized_categories = {"categories": serialized_categories}
    response = make_response(jsonify(serialized_categories))
    response.headers['Content-type'] = 'application/json'
    return response


@app.route("/categories.json")
def categories_json():
    """json output of all the categories without its items"""
    categories = session.query(Category).all()
    serialized_categories = [category.serialize for category in categories]
    response = make_response(jsonify(serialized_categories))
    response.headers['Content-type'] = 'application/json'
    return response


@app.route("/catalog/<category_id>/json/")
def category_items_json(category_id):
    """json output of the category"""
    category = session.query(Category).filter_by(id=category_id).first()
    response = make_response(jsonify(category.serialize))
    response.headers['Content-type'] = 'application/json'
    return response


@app.route("/catalog/<category_id>/<item_id>/json/")
def item_json(category_id, item_id):
    """json output of specific item in the category"""
    item = session.query(Item).filter_by(id=item_id).one()
    response = make_response(jsonify(item.serialize))
    response.headers['Content-type'] = 'application/json'
    return response


@app.route("/catalog/<item_id>/edit/", methods=["GET", "POST"])
def edit(item_id):
    """Edits the selected item"""
    if logged_in():
        item = session.query(Item).filter_by(id=item_id).first()
        user_id = getUserID(login_session['email'])

        # check if the item exists
        if item is not None:
            # if the logged in person is not the owner of the item,
            # do not let them delete the item
            if item.user_id != user_id:
                flash('Unauthorized Access')
                return redirect(url_for('catalog'))
            # if it is a post method, delete it from the database
            if request.method == "POST":
                title = request.form.get('title').strip()
                description = request.form.get('description')
                cat_id = request.form.get('cat_id')

                # only update if they changed one of the fields. avoids db hits
                if item and (item.description != description or
                             str(item.cat_id) != cat_id or
                             item.title != title):

                    # only update the title if they
                    # provided a title that is not empty
                    if title:
                        item.title = title
                    item.description = description
                    item.cat_id = cat_id
                    session.add(item)
                    session.commit()
                    flash("You have updated %s" % item.title)
                    return redirect(url_for('item', category_id=item.cat_id,
                                    item_id=item_id))
                else:
                    # if there was no change, flash error message
                    flash("You didnt change anything!")
                    return redirect(url_for('edit', item_id=item_id))

            # if get method, render the edit.html page
            categories = session.query(Category).all()
            return render_template('edit.html', item=item,
                                   categories=categories,
                                   logged_in=logged_in())
        # if the item does not exist, let the user know
        else:
            flash("Item %s does not exist" % item_id)
            return redirect(url_for('catalog'))
    else:
        flash('Unauthorized Access')
        return redirect(url_for('catalog'))


@app.route("/catalog/<item_id>/delete/", methods=["GET", "POST"])
def delete(item_id):
    """Deletes the selected item"""
    if logged_in():
        item = session.query(Item).filter_by(id=item_id).first()
        user_id = getUserID(login_session['email'])

        # check if the item exists
        if item is not None:
            # if the logged in person is not the owner of the item,
            # do not let them delete the item
            if item.user_id != user_id:
                flash('Unauthorized Access')
                return redirect(url_for('catalog'))
            # if it is a post method, delete it from the database
            if request.method == "POST":
                session.delete(item)
                session.commit()
                flash('Item was deleted')
                return redirect(url_for('catalog'))
            # if get method, show the button to confirm deletion
            return render_template('delete.html', item=item,
                                   logged_in=logged_in())
        # if the item does not exist, let the user know
        else:
            flash("Item %s does not exist" % item_id)
            return redirect(url_for('catalog'))
    else:
        flash('Unauthorized Access')
        return redirect(url_for('catalog'))


@app.route("/catalog/new/", methods=["GET", "POST"])
def new():
    """Creates a new item"""

    if logged_in() and request.method == 'POST':
        # check to see if they entered a title
        if request.form.get('title'):
            # get the category and description and enter it into the database
            title = request.form.get('title')
            cat_id = request.form.get('category')
            description = request.form.get('description')
            user_id = getUserID(login_session['email'])
            item = Item(cat_id=cat_id, title=title, description=description,
                        user_id=user_id)
            session.add(item)
            session.commit()
            # flash a message to let them know the item has been created
            flash("You have added a new item! category id: %s , title: %s,"
                  "description: %s" % (cat_id, title, description))
            return redirect(url_for('catalog'))
    else:
        # show the 'new' form
        categories = session.query(Category).all() if logged_in() else None
        return render_template('new.html', categories=categories,
                               logged_in=logged_in())


@app.route('/login/')
def showLogin():
    """Generates a state and shows a login page"""

    # create a random string state to prevent cross site forgery
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    # save state in session
    login_session['state'] = state
    return render_template('login.html', STATE=state)


def getUserID(email):
    """Get a user's id based on email"""
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except exc.SQLAlchemyError:
        return None


def getUserInfo(user_id):
    """get a user based on their id"""
    try:
        user = session.query(User).filter_by(id=user_id).first()
        return user
    except exc.SQLAlchemyError:
        return None


def createUser(login_session):
    """creates a new user using the info stored in the
    login_session and saves it in the database"""
    newUser = User(email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


@app.route('/gconnect', methods=["POST"])
def gconnect():
    """Connect using google login"""
    state = request.args.get('state')
    # if the state is not the same, then reject connection
    if state != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-type'] = 'application/json'
        return response

    # if the state tokens match, then get the google one time use code
    code = request.data
    try:
        # CLIENT_ID = os.environ.get('ITEM_CATALOG_GOOGLE_ID')
        # CLIENT_SECRET = os.environ.get('ITEM_CATALOG_GOOGLE_SECRET')
        CLIENT_ID = json.loads(open('client_secrets.json',
                                    'r').read())['web']['client_id']
        CLIENT_SECRET = json.loads(open('client_secrets.json',
                                   'r').read())['web']['client_secret']
        # upgrade the authorization code into a credentials object
        # oauth_flow = flow_from_clientsecrets('client_secrets.json',scope='')
        oauth_flow = OAuth2WebServerFlow(client_id=CLIENT_ID,
                                         client_secret=CLIENT_SECRET,
                                         scope='',
                                         redirect_uri='postmessage')
        credentials = oauth_flow.step2_exchange(code)
    # if unable to exchange authorization code for credentials, give error
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the '
                                            'authorization code.'), 401)
        return response
    # if able to trade for credentials, check if access_token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    # result contains our client id and the logged in user's info
    result = json.loads(h.request(url, 'GET')[1].decode())

    # if there is an error in the access token, then give error response
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-type'] = 'application/json'
        return response

    # if ther were no issues with the state or exchanging for access token,
    # check to see if the access token's id matches the google user id
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID does not match "
                                            "given user ID"), 401)
        response.headers['Content-type'] = 'application/json'
        return response

    # verify that the access token is valid for our app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's user ID doesn't match "
                                            "app's ID"), 401)
        response.headers['Content-type'] = 'application/json'
        return response

    # check to see if user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    # if these 2 are stored and matches, then the user is already logged in
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('User is already connected'), 200)
        response.headers['Content-type'] = 'application/json'
        return response

    # if access token user matches logged in user and client id matches
    # client id, get the user info from google
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    # store the users info in login_session
    login_session['provider'] = 'google'
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # check to see if user is found in database and
    # then populate the login_session['user_id']
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    user = getUserInfo(user_id)
    login_session['user_id'] = user.id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    return output


@app.route('/gdisconnect/')
def gdisconnect():
    """Disconnects a connected google logged in user"""
    # only disconnect a connected user
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user is not '
                                            'connected'), 401)
        response.headers['Content-type'] = 'application/json'
        return response

    # if the user is connected, get the access token and revoke it
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    # if revoking was successful, reset the user's sessions and send response
    del login_session['gplus_id']
    del login_session['access_token']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['provider']

    return redirect(url_for('catalog'))


if __name__ == '__main__':

    app.debug = debug
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
