# Introduction
Item Catalog is an app that provides a list of items within a variety of categories, as well as provide a user registration and authentication system through google login.

This project is viewable at https://lz-item-catalog.herokuapp.com

## Installation
1. python3.5

2. flask

3. sqlalchemy

4. json

5. oauth2client.client

6. httplib2

7. requests

8. os

## Usage
1. Run the project
```python views.py```
2. Go on your web browser to http://localhost:8000

## Description
* Homepage displays all current categories along with the latest added items.
* Selecting a specific category shows you all the items available for that category.
* After logging in, a user has the ability to add, update, or delete item info.
* The application provides a JSON endpoint of all categories and items: https://lz-item-catalog.herokuapp.com/catalog.json
