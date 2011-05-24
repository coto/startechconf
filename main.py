#!/usr/bin/env python2.5
##
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
import datetime, re, languages, captcha, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from google.appengine.dist import use_library
use_library('django', '0.96')

from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp \
	import util, template

from string import *

import logging

def get_country(self):
    try:
        raw = urlfetch.fetch("http://api.hostip.info/get_html.php?ip="+self.request.remote_addr)
    except:
        return "XX"
    country = ""
    try:
        country = raw.content.split('(')[1]
        country = country.split(')')[0]
    except:
        country = "XX"
    return country

def isAddressValid(email):
    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
            return 1
    return 0

def get_device(self):
    uastring = self.request.user_agent
    return "desktop"

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
    lang = {
	  'en': languages.en,
	  'es': languages.es,
	  'pt': languages.pt
	}[lang_cookie]
    return lang

class Register(db.Model):
    email = db.StringProperty(required=True)
    when = db.DateTimeProperty(auto_now_add=True)
    remote_addr = db.StringProperty(required=True)
    language = db.StringProperty()
    country = db.StringProperty()

def we_are():
    return db.GqlQuery(
		'SELECT * FROM Register '
		'ORDER BY when DESC')		

class MainHandler(webapp.RequestHandler):
    def get(self):
        chtml = captcha.displayhtml(
		  public_key = "6Lc_FsMSAAAAAHTVnQXGrWvzdshrKixBJghOgl3O",
		  use_ssl = False,
		  error = None)
        params = {
			'device': get_device(self),
			'path' : self.request.path,
			'count': we_are().count(),
			'lang': set_lang_cookie_and_return_dict(self.request, self.response),
			'captchahtml': chtml,
		}
        self.response.out.write(
			template.render('index.html', params))

class RegisterHandler(webapp.RequestHandler):

    def get(self):
        self.redirect("/")

    def post(self):
        # ***** Damain Control *****
        if self.request.referer.find("http://localhost") == -1 and self.request.referer.find("http://www.startechconf.com/") == -1:
            self.redirect("/?error=fake")
            return

        # ***** Define some variables *****
        lang = set_lang_cookie_and_return_dict(self.request, self.response)
        ip = self.request.remote_addr
        now = datetime.datetime.now()
        email = self.request.get("email")
        challenge = self.request.get('recaptcha_challenge_field')
        response  = self.request.get('recaptcha_response_field')

        cResponse = captcha.submit(
						 challenge,
						 response.encode('utf-8'),
						 "6Lc_FsMSAAAAAEeoIjOaGU_M0obCkgDPbIevfUUV",
						 ip)

        logging.info(cResponse.error_code)
        if not cResponse.is_valid:
            params = {
				'device': get_device(self),
				'path' : self.request.path,
				'count': we_are().count(),
				'lang': lang,
				'msg': lang["invalid_captcha"],
				'is_error': True
			}
            self.response.out.write(
				template.render('index.html', params))
            return

        logging.info(email)
        # ***** Email Verification *****
        if not isAddressValid(email):
            params = {
				'device': get_device(self),
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
					'device': get_device(self),
					'path' : self.request.path,
					'count': we_are().count(),
					'lang': lang,
					'msg': lang["already_registered"],
					'is_error': False
				}
                self.response.out.write(
					template.render('index.html', params))
            else:
                register = Register(
					email = email,
					remote_addr = ip,
					language = lang["id"],
					country = get_country(self)
				)
                register.put()

                # Internal
                message_to_admin = mail.EmailMessage()
                message_to_admin.sender = "contact@startechconf.com"
                message_to_admin.subject = "StarTechConf - Preregister"
                message_to_admin.to = "rodrigo.augosto@gmail.com, contact@startechconf.com"
                message_to_admin.body = '{\n\t"email": "%(email)s", \n\t"when": "%(when)s", \n\t"remote_addr": "%(remote_addr)s", \n\t"language": "%(language)s, \n\t"country": "%(country)s"\n},' % \
						  {'email': email, "when": str(now), "remote_addr": ip, "language": lang["id"], "country": get_country(self)}
                message_to_admin.send()


                #External
                message_to_user = mail.EmailMessage()
                message_to_user.sender = "contact@startechconf.com"
                message_to_user.subject = lang["registered_email_subject"]

                logging.info(message_to_user.subject)

                message_to_user.to = email
                message_to_user.body = lang["registered_email_body"]

                logging.info(message_to_user.body)

                message_to_user.send()

                params = {
					'device': get_device(self),
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
			'device': get_device(self),
			'count': we_are().count(),
			'path' : self.request.path,
			'lang': set_lang_cookie_and_return_dict(self.request, self.response)
		}		
        self.response.out.write(template.render('organizers.html', params))

class Counter(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            greeting = ("Welcome, %s! <a href=\"%s\">sign out</a><h1 style=\"font-size: 5em;\">we are: %s</h1>" %
						(user.nickname(), users.create_logout_url(self.request.path), str(we_are().count())))
        else:
            greeting = ("<a href=\"%s\">Sign in or register</a>." %
						users.create_login_url(self.request.path))

        self.response.out.write("<html><body>%s</body></html>" %
								(greeting))

def main():
    application = webapp.WSGIApplication([
		('/', MainHandler),
		('/[R|r]egister', RegisterHandler),
		('/counter', Counter),
		#('/[O|o]rganizers', OrganizersHandler),
	], debug=False)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
