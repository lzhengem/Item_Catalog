# Introduction
Item Catalog is an app that provides a list of items within a variety of categories, as well as provide a user registration and authentication system through google login.

This project is viewable at https://lz-item-catalog.herokuapp.com

## Installation
1. python3.5: Download from https://www.python.org/downloads/

2. flask

```pip3 install flask```

3. sqlalchemy

```pip3 install sqlalchemy```

4. oauth2client

```pip3 install oauth2client```

5. sqlalchemy_utils

```pip3 install sqlalchemy_utils```

6. psycopg2-binary

```pip3 install psycopg2-binary```

## Usage
1. Create the database and objects

```python3 models.py```

2. Create the categories

```python3 insert_categories.py```

3. Run the project

```python3 views.py```

4. Go on your web browser to http://localhost:8000

## Description
* Homepage displays all current categories along with the latest added items.
* Selecting a specific category shows you all the items available for that category.
* After logging in, a user has the ability to add, update, or delete item info.
* The application provides a JSON endpoint of all categories and items: https://lz-item-catalog.herokuapp.com/catalog.json
