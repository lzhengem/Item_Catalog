from flask import Flask

app = Flask(__name__)

#lists all the categories
@app.route("/")
@app.route("/catalog/")
def homepage():
    return "You are at the homepage!"

#a json output of all the categories
@app.route("/catalog.json")
def category_json():
    return "You are at the category json page!"

#added items in selected category
@app.route("/catalog/<category>/items/")
def category_items(category):
    return "You are viewing %s items!" % category

#specifit item in the category
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




if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0',port=8000)