# Introduction
Item Catalog is an app that provides a list of items within a variety of categories, as well as provide a user registration and authentication system through google login.

<!-- This project is viewable at https://lz-item-catalog.herokuapp.com -->

## Installation
1. python3.5: Download from https://www.python.org/downloads/
2. flask
    * ```pip3 install flask```
3. sqlalchemy
    * ```pip3 install sqlalchemy```
4. oauth2client
    * ```pip3 install oauth2client```
5. sqlalchemy_utils
    * ```pip3 install sqlalchemy_utils```
6. psycopg2-binary
    * ```pip3 install psycopg2-binary```

## Usage
1. Create the database and objects
    * ```python3 models.py```
2. Insert categories into database
    * ```python3 insert_categories.py```
3. Run the project
    * ```python3 views.py```
4. Go on your web browser to http://localhost:8000. Recommended browser is Chrome.
5. If the login button does not show up in http://localhost:8000/login, then make sure to clear your cache.


## Amazon lightsail and Apache setup

### Third party resources:
1. Apache
2. WSGI
3. Amazon Lightsail

### Setup
1. Made an AWS account from Amazon
2. Create Ubuntu 16.04 LTS instance
    * The public IP is [35.167.198.96](http://35.167.198.96)
3. Update and upgrade the lightsail instance
    * ```sudo apt-get update```
    * ```sudo apt-get upgrade  ```
4. Install apache
    * ```sudo apt-get install apache2```
5. Install and enable mod_wsgi
    * ```sudo apt-get install libapache2-mod-wsgi-py3```
    * ```sudo a2enmod wsgi```
6. Install postgresql
    * ```sudo apt-get install postgresql```
7. Create user 'grader' on lightsail
    * ```sudo adduser grader```
8. Give grader sudo powers
    * Create the file /etc/sudoers.d/grader with the following text:
        ```
        # Created by cloud-init v. 17.2 on Sun, 24 Mar 2019 02:34:14 +0000
        # User rules for grader
        grader ALL=(ALL) NOPASSWD:ALL
        ```
9. On vagrant machine used ssh-keygen to generate a private public key pair and saved it in \~/.ssh/lightsail_grader
    * ```ssh-keygen```
    * This will generate 2 files where the .pub is the public key:
        * \~/.ssh/lightsail_grader 
        * \~/.ssh/lightsail_grader.pub
10. Install the public key on the lighsail server
    * copy the key generated on our vagrant machine (lightsail_grader.pub) to lightsail /home/grader/.ssh/authorized_keys
11. Disable root login
    * Edit /etc/ssh/sshd_config, changing PermitRootLogin to no
12. Force users to ssh for login
    * Edit /etc/ssh/sshd_config:
        * RSAAuthentication yes
        * PubkeyAuthentication yes
        * PasswordAuthentication no
13. Change the ssh port from 22 to 2200:
    * Add a custom port 2200 in lightsail: https://lightsail.aws.amazon.com/ls/webapp/us-west-2/instances/lz-item-catalog/networking
    * Edit the /etc/ssh/sshd_config from Port 22 to Port 2200
    * Restart the sshd service: ```sudo service sshd restart```
14. Set up the firewall to only allow ports 2200, 80, 123:
    * ```sudo ufw default deny incoming```
    * ```sudo ufw status```
    * ```sudo ufw default deny incoming```
    * ```sudo ufw default allow outgoing```
    * ```sudo ufw allow ssh```
    * ```sudo ufw allow 2200/tcp```
    * ```sudo ufw allow www```
    * ```sudo ufw allow 123/udp```
    * ```sudo ufw deny 22```
    * ```sudo ufw enable```
    * reboot the amazon lightrail server: https://lightsail.aws.amazon.com/ls/webapp/us-west-2/instances/lz-item-catalog/connect
15. Cloned Item_Catalog into /var/www/FlaskApps
16. Setting up wsgi
    * Create the file /var/www/FlaskApp/flaskapp.wsgi
        * flaskapp.wsgi will import from the Item_Catalog \_\_init\_\_.py file
    * Create /etc/apache2/sites-available/FlaskApp.conf file to configure which is root directory
    * enable the FlaskApp: ```sudo a2ensite FlaskApp```
17. Setting up postgresl
    * Create psql user ubuntu
    * Grant permissions to item_catalog to ubuntu
18. Created \_\_init\_\_.py file which is the main driver of apache project


## Description
* Homepage displays all current categories along with the latest added items.
* Selecting a specific category shows you all the items available for that category.
* After logging in, a user has the ability to add, update, or delete item info.
* The application provides a JSON endpoint of all categories and items: <!-- https://lz-item-catalog.herokuapp.com/catalog.json -->
