heroku steps:
$heroku create lz-item-catalog
#get installed python packages for requirements.txt file
$pip freeze
#created Procfile, runtime.txt, requirements.txt

#set up dynos
$heroku ps:scale web=1

#create postgres database on heroku
$heroku addons:create heroku-postgresql:hobby-dev

#log into heroku's postgres - be in the vagrant environment when running this
$ heroku pg:psql

#get the url to your heroku database
$DATABASE_URL=$(heroku config:get DATABASE_URL -a lz-item-catalog)

#set up test envionment on mac: --add this to .bash_rc
$export FLASK_ENV=development

#set up prod environment on heroku:
$heroku config:set FLASK_ENV=production

#show you env variables on heroku
$ heroku config

#next, update models.py, views.py, insert_categories.py so that if it is production (heroku), then it uses the production database link
import os

if os.getenv('FLASK_ENV') == 'development':
    engine = create_engine('postgresql+psycopg2:///item_catalog')
elif os.getenv('FLASK_ENV') == 'production':
    database_url = os.getenv('DATABASE_URL')
    engine = create_engine(database_url)

#create the models in the heroku database
$heroku run python3 models.py

#insert categories into heroku database
$ heroku run python3 insert_categories.py

#change port to heroku's perferred port -changed in views.py
    app.debug = debug
    port = int(os.environ.get('PORT',8000))
    app.run(host='0.0.0.0',port=port)

#add the google id and google client environment for project
heroku config:set ITEM_CATALOG_GOOGLE_ID={enter id here}
heroku config:set ITEM_CATALOG_GOOGLE_SECRET={enter secret here}

