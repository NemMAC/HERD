#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os
import json
import random
import urllib2
import logging
from google.appengine.api import users
from google.appengine.ext import ndb

"""
Milans Space. Dont touch.
"""

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


# LOGIN
class Login(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            nickname = user.nickname()
            logout_url = users.create_logout_url('/')
            greeting = 'Welcome, {}! (<a href="{}">sign out</a>)'.format(
                nickname, logout_url)
        else:
            login_url = users.create_login_url('/map')
            greeting = '<a href="{}">Sign in</a>'.format(login_url)

        self.response.write(
            '<html><body>{}</body></html>'.format(greeting))
        template = jinja_environment.get_template('cover.html')
        self.response.out.write(template.render())

class AdminPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            if users.is_current_user_admin():
                self.response.write('You are an administrator.')
            else:
                self.response.write('You are not an administrator.')
        else:
            self.response.write('You are not logged in.')

# MAP
class Map(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('map.html')
        self.response.out.write(template.render())

#About

class About(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('about.html')
        self.response.out.write(template.render())



# DATASTORE

class Location(ndb.Model):
    UserID = ndb.StringProperty()
    lat = ndb.FloatProperty()
    lng = ndb.FloatProperty()

class Store(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        UserID = user.user_id()
        logging.info ('user is: ')
        logging.info (UserID)

        if user:
            lat = float(self.request.get('lat'))
            lng = float(self.request.get('lng'))
            logging.info ('location got')
            logging.info ('user is: ')
            logging.info (UserID)

            exist = Location.query(Location.UserID==user.user_id()).get()
            # Let's first check if this user already exists in the database
            # If they do, get that entry (its key) and modify it
            if exist:
                update = exist
                update.lat = lat
                update.lng = lng
            else:
                update = Location(UserID=user.user_id(), lat=lat, lng=lng)
            update.put()
            logging.info('location store')

    def get(self):
        query = Location.query()
        results = query.fetch()
        resultdict = [i.to_dict() for i in results]
        self.response.out.write(json.dumps(resultdict))
        logging.info('result is: ')
        logging.info(resultdict)






app = webapp2.WSGIApplication([
('/', Login),
('/map', Map),
('/about', About),
('/datastore', Store)

], debug=True)
