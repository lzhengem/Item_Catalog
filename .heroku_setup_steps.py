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