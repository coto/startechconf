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
import datetime, re

from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp \
	import util, template
	
from google.appengine.ext.webapp.util import login_required
from string import *

import languages

rfc822_specials = '()<>@,;:\\"[]'

def isAddressValid(email):
	if len(email) > 7:
		if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
			return 1
	return 0

class Register(db.Model):
  email = db.StringProperty(required=True)
  when = db.DateTimeProperty(auto_now_add=True)
  remote_addr = db.StringProperty(required=True)

def set_lang_cookie_and_return_dict(request, response):
	lang_cookie = "en"
	if request.get("hl") == "":
		# ask for cookie
		lang_cookie = request.cookies.get("hl")
		if not lang_cookie:
			lang_cookie = "en"
	else:
		# set cookie to en
		lang_cookie = request.get("hl")
	
	response.headers.add_header("Set-Cookie", "hl=" + lang_cookie + ";")
	return languages.en if lang_cookie == "en" else languages.es

def we_are():
	return db.GqlQuery(
		'SELECT * FROM Register '
		'ORDER BY when DESC')		

class MainHandler(webapp.RequestHandler):
	def get(self):
		uastring = self.request.user_agent
		params = {
			'device': 'desktop',
			'uastring': uastring,
			'path' : self.request.path,
			'count': we_are().count(),
			'lang': set_lang_cookie_and_return_dict(self.request, self.response)
		}
		self.response.out.write(
			template.render('index.html', params))

class RegisterHandler(webapp.RequestHandler):
	
	def get(self):
		self.redirect("/")
		
	def post(self):
		uastring = self.request.user_agent
		if not self.request.referer.find("://localhost") < 5 or not self.request.referer.find("startechconf.com") < 10:
			self.redirect("/")
			return
		
		lang = set_lang_cookie_and_return_dict(self.request, self.response)
		
		ip = self.request.remote_addr
		now = datetime.datetime.now()
		email = self.request.get("email")
		
		if not isAddressValid(email):
			params = {
				'device': 'desktop',
				'uastring': uastring,
				'path' : self.request.path,
				'count': we_are().count(),
				'lang': lang,
				'msg': lang["invalid_email_address"],
				'is_error': False				
			}
			self.response.out.write(
				template.render('index.html', params))
		else:
			registers = db.GqlQuery(
				"SELECT * FROM Register "
				"WHERE email = :1", email)
			bot = registers.count()
			if bot >= 1:
				params = {
					'device': 'desktop',
					'uastring': uastring,
					'path' : self.request.path,
					'count': we_are().count(),
					'lang': lang,
					'msg': lang["already_registered"],
					'is_error': False
				}
				self.response.out.write(
					template.render('index.html', params))
			else:		
				message = mail.EmailMessage()
				message.sender = "contact@startechconf.com"
				message.subject = "StarTechConf - Preregister"
		
				# Internal
				message.to = "rodrigo.augosto@gmail.com, contact@startechconf.com"
				message.body = '{\n\t"email": "%(email)s", \n\t"when": "%(when)s", \n\t"remote_addr": "%(remote_addr)s"\n},' % \
				          {'email': email, "when": str(now), "remote_addr": ip}
				message.send()
		
				#External 
				message.to = email
				message.body = """<p>Hey, Thank you for preregistering, keep following our twitter: http://twitter.com/startech2011
				in order to know when Inscriptions will be open.</p>
				<br/><br/>
				<p>Gracias por preregistrarte en StarTech Conference, sigue nuestro twitter: http://twitter.com/startech2011
				para saber cuando van a abrise las inscripciones.</p>
				"""
				message.send()
				register = Register(
					email = email,
					remote_addr = ip
				)
				register.put()
				params = {
					'device': 'desktop',
					'uastring': uastring,
					'path' : self.request.path,
					'count': we_are().count(),
					'lang': lang,
					'msg': lang["successfuly_registered"],
					'is_error': False
				}
				self.response.out.write(
					template.render('index.html', params))

class OrganizersHandler(webapp.RequestHandler):
	def get(self):
		params = {
			'device': 'desktop',
			'count': we_are().count(),
			'path' : self.request.path,
			'lang': set_lang_cookie_and_return_dict(self.request, self.response)
		}		
		self.response.out.write(template.render('organizers.html', params))

def main():
    application = webapp.WSGIApplication([
		('/', MainHandler),
		('/[R|r]egister', RegisterHandler)
		#('/[O|o]rganizers', OrganizersHandler)
	], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
