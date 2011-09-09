#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2010 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""A barebones AppEngine application that uses Facebook for login."""

##### Facebook
FACEBOOK_APP_ID = "170575249681923"
FACEBOOK_APP_SECRET = "l2AoXTehXt6ob0QPVML8Fq9UyedOXXiJ1j67LOWUgk"

#Twitter
CONSUMER_KEY = 'IMcyLHus0j3GjOFQy8Zonw'
CONSUMER_SECRET = 'bHb6voZZw7xnySNfXCtpWAdFQmMJV2BXxJ6KrQgCiE'
CALLBACK = 'http://www.startechconf.com/participa'

from libs import facebook
import os, languages
import os.path
import wsgiref.handlers
import sys
from google.appengine.api import urlfetch
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
import unicodedata

#twitter
sys.path.insert(0, 'tweepy.zip')
import cgi
import pickle
from google.appengine.ext.webapp import RequestHandler
import tweepy
from tweepy.api import API
from google.appengine.ext.webapp.util import run_wsgi_app
import Cookie
from string import *

def get_country(self):
    country = urlfetch.fetch("http://geoip.wtanaka.com/cc/"+self.request.remote_addr).content
    return country

def set_lang_cookie_and_return_dict(self):
    if self.request.get("hl") == "":
        # ask for cookie
        lang_cookie = self.request.cookies.get("hl")
        c = get_country(self)
        if not lang_cookie:
            if c == "ca" or c == "uk" or c == "us" or c == "eu" or c == "de" \
               or c == "gb" or c == "jp" or c == "cn" or c == "in" or c == "ru" \
               or c == "no" or c == "au" or c == "nz" or c == "se" or c == "dk":
                lang_cookie = "en"
            elif c == "br" or c == "pt":
                lang_cookie = "pt"
            else:
                lang_cookie = "es"
    else:
        lang_cookie = self.request.get("hl")

    self.response.headers.add_header("Set-Cookie", "hl=" + lang_cookie + ";")
    lang = {
	  'en': languages.en,
	  'es': languages.es,
	  'pt': languages.pt
	}[lang_cookie]
    return lang


class User(db.Model):
    id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    profile_url = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)

class Posts(db.Model):
    id_autor = db.StringProperty(required=True)
    nombre = db.StringProperty(required=True)
    msj = db.TextProperty(required=True)
    fecha = db.DateTimeProperty(auto_now_add=True)
    network = db.StringProperty(required=True, default="null")

class OAuthToken(db.Model):
    token_key = db.StringProperty(required=True)
    token_secret = db.StringProperty(required=True)

class BaseHandler(webapp.RequestHandler):
    """Provides access to the active Facebook user in self.current_user

    The property is lazy-loaded on first access, using the cookie saved
    by the Facebook JavaScript SDK to determine the user ID of the active
    user. See http://developers.facebook.com/docs/authentication/ for
    more information.
    """
    @property
    def current_user(self):
        if not hasattr(self, "_current_user"):
            self._current_user = None
            cookie = facebook.get_user_from_cookie(self.request.cookies, FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)
            if cookie:
                # Store a local instance of the user data so we don't need
                # a round-trip to Facebook on every request
                user = User.get_by_key_name(cookie["uid"])
                if not user:
                    graph = facebook.GraphAPI(cookie["access_token"])
                    profile = graph.get_object("me")
                    user = User(key_name=str(profile["id"]),
                                id=str(profile["id"]),
                                name=profile["name"],
                                profile_url=profile["link"],
                                access_token=cookie["access_token"])
                    user.put()
                elif user.access_token != cookie["access_token"]:
                    user.access_token = cookie["access_token"]
                    user.put()
                self._current_user = user
        return self._current_user

# Twitter handler  (/oauth/)
class TwitterOauth(RequestHandler):
    def get(self):
        # Build a new oauth handler and display authorization url to user.
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK)
        go_url = auth.get_authorization_url(True)
        auth.request_token

        # We must store the request token for later use in the callback page.
        request_token = OAuthToken(
            token_key = auth.request_token.key,
            token_secret = auth.request_token.secret
        )
        request_token.put()
        #Redirect
        self.redirect(go_url)


# Twitter logout  (/salir/)
class TwitterLogout(RequestHandler):
    def get(self):
        # Set cookie with negative value
        self.response.headers.add_header('Set-Cookie', 'startech=; path = /; expires=Fri, 12-Aug-1999 23:59:59 GMT')
        self.redirect('/participa')

class HomeHandler(BaseHandler):
	def slugify(s):
		return ''.join(unicodedata.normalize("NFD",c)[0] for c in s)

	@property
	def current_user_twitter(self):
		self._current_user_twitter = None
		oauth_token = self.request.get("oauth_token")
		oauth_verifier = self.request.get("oauth_verifier")
		if oauth_token is None:
			return
		# Lookup the request token
		request_token = OAuthToken.gql("WHERE token_key=:key", key=oauth_token).get()
		if request_token is None:
			return
		# Rebuild the auth handler
		auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
		auth.set_request_token(request_token.token_key, request_token.token_secret)
		# Fetch the access token
		try:
			auth.get_access_token(oauth_verifier)
		except tweepy.TweepError, e:
			return
		# So now we could use this auth handler.
		# Here we will just display the access token key&secret
		twitterapi = tweepy.API(auth)
		user = twitterapi.me()

		userb = User(key_name=user.screen_name,
					id=user.screen_name,
					name=user.screen_name,
					profile_url=user.screen_name,
					access_token=str(auth.access_token))
		userb.put()
		self._current_user_twitter = userb

		return self._current_user_twitter


	def get(self):
		q_count = None
		cutt = self.current_user_twitter
		# Check is user is logged in (FB)
		if self.current_user:
			# Check if the user is already participating
			uid = self.current_user.id
			q_uid = db.GqlQuery("SELECT * FROM Posts WHERE id_autor = :1", uid)
			q_count = q_uid.count()
		else:
			# Check if the user is logged in (TT)
			if cutt:
				if self.request.get("oauth_token") is not None:
					# Set cookie
					cookie = '%s|%s' % (cutt.id, cutt.access_token)
					self.response.headers.add_header('Set-Cookie', 'startech=%s; expires=Fri, 31-Dec-2020 23:59:59 GMT' % cookie.encode())
					self.redirect('/participa')
					return
			else:
				# Read from cookie
				startech = self.request.cookies.get('startech')
				if startech is not None:
					cookie_args = list()
					cookie_args = split(startech, '|')
					userb = User(key_name=cookie_args[0],
							id=cookie_args[0],
							name=cookie_args[0],
							profile_url=cookie_args[0],
							access_token=str(cookie_args[1]))
					# Check if cookie data matches DB
					checkuser = db.GqlQuery("SELECT * FROM User WHERE id = :1 AND access_token = :2", userb.id, userb.access_token)
					if checkuser.count() == 1:
						cutt = userb
						# Check user posts
						q_uid = db.GqlQuery("SELECT * FROM Posts WHERE id_autor = :1", userb.id)
						q_count = q_uid.count()
		# Get last 12 posts
		q = db.GqlQuery("SELECT * FROM Posts ORDER BY fecha DESC")
		last_posts = q.fetch(20)
		for post in last_posts:
			if post.id_autor.isdigit():
				post.profile_img = 'http://graph.facebook.com/%s/picture' % (post.id_autor)
			else:
				post.profile_img = 'http://api.twitter.com/1/users/profile_image?screen_name=%s' % (post.id_autor)
		# Render template
		path = os.path.join(os.path.dirname(__file__), "participa.html")
		args = dict(lang=set_lang_cookie_and_return_dict(self), current_user=self.current_user, current_user_twitter=cutt, facebook_app_id=FACEBOOK_APP_ID, authurl='/oauth/', last_posts=last_posts, already=q_count)
		self.response.out.write(template.render(path, args))

	def post(self):
		q_count = None
		# Check is user is logged in
        # FACEBOOK
		if self.current_user:
			# Check if the user is already participating
			uid = self.current_user.id
			q_uid = db.GqlQuery("SELECT * FROM Posts WHERE id_autor = :1", uid)
			q_count = q_uid.count()
			if not q_count:
				# Get Form data
				msg = self.request.str_POST["content"]
				msg = unicode(msg, 'utf-8')
				# Check length restrictions
				if len(msg) > 140:
					self.redirect('/participa')
					return
				elif len(msg) < 5:
					self.redirect('/participa')
					return
				else:
					graph = facebook.GraphAPI(self.current_user.access_token)
					profile = graph.get_object("me")
					new_post = Posts(id_autor = profile["id"], nombre = profile["name"], msj = msg, network = "facebook")
					new_post.put()
					fb_response = graph.put_wall_post(msg.encode('utf-8'))
		else:
            # TWITTER
			cutt = None
			# Read from cookie
			startech = self.request.cookies.get('startech')
			if startech is not None:
				cookie_args = list()
				cookie_args = split(startech, '|')
				userb = User(key_name=cookie_args[0],
						id=cookie_args[0],
						name=cookie_args[0],
						profile_url=cookie_args[0],
						access_token=str(cookie_args[1]))
				# Check if cookie data matches DB
				checkuser = db.GqlQuery("SELECT * FROM User WHERE id = :1 AND access_token = :2", userb.id, userb.access_token)
				if checkuser.count() == 1:
					cutt = userb
			if cutt:
				# Check if the user is already participating
				uid = cutt.id
				q_uid = db.GqlQuery("SELECT * FROM Posts WHERE id_autor = :1", uid)
				q_count = q_uid.count()
				if not q_count:
					# Get Form data
					msg = self.request.str_POST["content"]
					msg = unicode(msg, 'utf-8')
					# Check length restrictions
					if len(msg) > 140:
						self.redirect('/participa')
						return
					elif len(msg) < 5:
						self.redirect('/participa')
						return
					else:
						msg += ' #startechconf'
						# Normally the key and secret would not be passed but rather
						# stored in a DB and fetched for a user.
						tokens = list()
						tokens = split(userb.access_token, '&')
						token_key = tokens[1].replace("oauth_token=", "")
						token_secret = tokens[0].replace("oauth_token_secret=", "")
						#Here we authenticate this app's credentials via OAuth
						auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
						#Here we set the credentials that we just verified and passed in.
						auth.set_access_token(token_key, token_secret)
						#Here we authorize with the Twitter API via OAuth
						twitterapi = tweepy.API(auth)
						#Here we update the user's twitter timeline with the tweeted text.
						twitterapi.update_status(msg.encode('utf-8'))
						new_post = Posts(id_autor = cutt.id, nombre = cutt.name, msj = msg, network = "facebook")
						new_post.put()
		self.redirect('/participa')

def main():
    util.run_wsgi_app(webapp.WSGIApplication([
		(r'/oauth/', TwitterOauth),
		(r'/salir/', TwitterLogout),
		(r"/participa", HomeHandler)
	]))


if __name__ == "__main__":
    main()
