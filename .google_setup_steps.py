notes:
-create an app with google developers
-get client id and key
-when making google log in, make sure to add 
    Authorized JavaScript origins:      http://localhost:8000, http://lz-item-catalog.herokuapp.com, https://lz-item-catalog.herokuapp.com
    and
    Authorized redirect URIs: http://localhost:8000/login http://localhost:8000/gconnect, http://lz-item-catalog.herokuapp.com/login, http://lz-item-catalog.herokuapp.com/gconnect, https://lz-item-catalog.herokuapp.com/login, https://lz-item-catalog.herokuapp.com/gconnect
-if getting the error:
    'app ____ is not an authorized endpoint blah blah blah' and you have already added that endpoint in google developer console,
    this might be because you have your app cached. go into private mode or clear your cache
