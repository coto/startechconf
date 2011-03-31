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

class MainHandler(webapp.RequestHandler):
    def get(self):
		registers = db.GqlQuery(
			'SELECT * FROM Register '
			'ORDER BY when DESC')
		uastring = self.request.user_agent
		if self.request.get("hl") == "":
			hl = "en"
		else:
			hl = self.request.get("hl")
		params = {
			'device': 'desktop',
			'uastring': uastring,
			'path' : self.request.path,
			'count': registers.count(),
			'hl': hl
		}
		if hl == "es":
			self.response.out.write(
				template.render('index-es.html', params))
		else:
			self.response.out.write(
				template.render('index.html', params))

class RegisterHandler(webapp.RequestHandler):
	def get(self):
		#registers = db.GqlQuery(
		#	'SELECT * FROM Register '
		#	'ORDER BY when DESC')
		#count = registers.count()
		#values = {
		#	'registers': registers,
		#	'count': count
		#}
		#self.response.out.write(template.render('register.html', values))
		self.redirect("/")
	def post(self):
		if not self.request.referer.find("://localhost") < 5 or not self.request.referer.find("startechconf.com") < 10:
			self.redirect("/")
			return
		ip = self.request.remote_addr
		now = datetime.datetime.now()
		email = self.request.get("email")
		if not isAddressValid(email):
			self.response.out.write("""doh! Please try to insert a valid email address, c'mon you can.<p><a href="/">Try again</a></p>""")
			return
		# Bot identifier
		registers = db.GqlQuery(
			"SELECT * FROM Register "
			"WHERE remote_addr = :1", ip)
		bot = registers.count()
		if bot >= 3:
			self.response.out.write("""<p>I'm sorry, but are you sure that you are not a Bot?</p> 
			<p>We know you'd love to attend, but take it easy, one pre-register is enough.</p>
			<p><a href="/">Go home</a></p>
			""")
			return
		# Already regitered identifier
		registers = db.GqlQuery(
			"SELECT * FROM Register "
			"WHERE email = :1", email)
		bot = registers.count()
		if bot >= 1:
			self.response.out.write("""<p>You are already registered. 
			Thank you and follow our twitter (<a href="http://www.twitter.com/startech2011">@startech2011</a>)</p>
			<p><a href="/">Go home</a></p>
			""")
			return
		
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
		message.body = "Hey, Thank you for preregister, keep following our twitter (@startech2011) in order to know when Inscriptions will be open."
		message.send()
		
		register = Register(
			email = email,
			remote_addr = ip
		)
		register.put()
		self.redirect("/?registered=ok")


def main():
    application = webapp.WSGIApplication([
		('/', MainHandler),
		('/[R|r]egister', RegisterHandler)
	], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
