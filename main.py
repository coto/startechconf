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
		uastring = self.request.user_agent
		ip = self.request.remote_addr
		now = datetime.datetime.now()
		user = users.get_current_user()
		path = self.request.path
		params = {
			'device': 'desktop',
			'uastring': uastring,
			'ip': ip,
			'user': user,
			'path' : path,
		}
		self.response.out.write(
			template.render('comingsoon.html', params))

class RegisterHandler(webapp.RequestHandler):
	def get(self):
		registers = db.GqlQuery(
			'SELECT * FROM Register '
			'ORDER BY when DESC')
		count = registers.count()
		values = {
			'registers': registers,
			'count': count
		}
		self.response.out.write(template.render('register.html', values))
	def post(self):
		ip = self.request.remote_addr
		now = datetime.datetime.now()
		email = self.request.get("email")
		registers = db.GqlQuery(
			"SELECT * FROM Register "
			"WHERE remote_addr = '127.0.0.1'")
		bot = registers.count()
		if bot > 5:
			self.response.out.write("I'm sorry, but are you sure that you are not a Bot? \n\nWe know you'd love to attend, but take it easy, one pre-register is enough.")
			return
		if not isAddressValid(email):
			self.response.out.write("doh! Please try to insert a valid email address, c'mon you can." + str(bot))
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
		self.response.out.write(temp)
		#self.redirect("/register")


def main():
    application = webapp.WSGIApplication([
		('/', MainHandler),
		('/[R|r]egister', RegisterHandler)
	], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()