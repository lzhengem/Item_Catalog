from flask import Flask

app = Flask(__name__)

@app.route("/")
def homepage():
    return "You are at the homepage!"

@app.route("/catalog/<category>/items/")
def catalog(category):
    return "You are viewing %s items!" % category

@app.route("/catalog/<category>/edit/")
def edit(category):
    return "You are viewing %s edit page!" % category


@app.route("/catalog/<category>/delete/")
def delete(category):
    return "You are viewing %s delete page!" % category


@app.route("/catalog/<category>/<item>/")
def item(category,item):
    return "You are viewing %s in %s!" % (item,category)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0',port=8000)