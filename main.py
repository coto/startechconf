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
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp \
	import util, template

def get_country(self):
    country = urlfetch.fetch("http://geoip.wtanaka.com/cc/"+self.request.remote_addr).content
    return country

def isAddressValid(email):
    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
            return 1
    return 0

def get_device(self):
    uastring = self.request.user_agent
    return "desktop"

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
			'lang': set_lang_cookie_and_return_dict(self),
			'captchahtml': chtml,
		}
        self.response.out.write(
			template.render('index.html', params))
    def post(self):
        self.redirect("/")

class OrganizersHandler(webapp.RequestHandler):
    def get(self):
        params = {
			'device': get_device(self),
			'count': we_are().count(),
			'path' : self.request.path,
			'lang': set_lang_cookie_and_return_dict(self)
		}		
        self.response.out.write(template.render('organizers.html', params))

class Counter(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        test = "text test"
        if user:
            greeting = ("Welcome, %s from %s! <a href=\"%s\">sign out</a><h1 style=\"font-size: 5em;\">we are: %s</h1><hr><div>%s</div>" %
						(user.nickname(), get_country(self), users.create_logout_url(self.request.path), str(we_are().count()), test))
        else:
            greeting = ("<a href=\"%s\">Sign in or register</a> from %s. <hr><div>%s</div>" %
						(users.create_login_url(self.request.path), get_country(self), test))

        self.response.out.write("<html><body>%s</body></html>" %
								(greeting))

class GetData(webapp.RequestHandler):
    def get(self):
        q = Register.all()
        q.order("when")
        user = users.get_current_user()
        data = ""
        if user:
            greeting = ("<a href=\"%s\">Sign out</a> <br>Welcome, %s!, If you are an administrator, you will see the table." %
                    (users.create_logout_url("/data"), user.nickname()))
            results = q.fetch(970)
            data = ""
            table = ""
            if users.is_current_user_admin():
                counter = 1

                for p in results:
                    ip = p.remote_addr
                    email = p.email
                    if email == "rodrigo.augosto@taisachile.cl":
                        email = "patriciomas@pixelkit.cl"
                    if email == "contact@protoboard.cl":
                        email = "eduardobaeza@pixelkit.cl"
                    #email = re.sub(r'.*\@(.+)', r'\1', email)
                    date = p.when.strftime("%A, %B %d, %Y ")
                    time = p.when.strftime("%I:%M:%S %p %Z")
                    datetime = p.when.strftime("%Y%m%d%H%M%S")
                    country = p.country

                    if country == None:
                        country = "__"

                    if country == "XX" or country == "":
                        country = urlfetch.fetch("http://geoip.wtanaka.com/cc/"+ip).content
                    language = p.language
                    country.upper()
                    table += "<tr><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % \
                            (counter, email, date, time, datetime, country, language, ip)
                    counter += 1

                data = """<table border=\"1\" cellspacing=\"0\">
                <tr style=\"background-color: #ccc;\">
                    <td>id</td><td>email</td><td>date</td><td>time</td><td>datetime<td>country</td><td>language</td><td>ip</td>
                </tr>
                %s</table>""" % (table)
        else:
            greeting = ("<a href=\"%s\">Sign in</a>." %
                    users.create_login_url("/data"))

        self.response.out.write("<html><body>%s %s</body></html>" % (greeting, data))

def main():
    application = webapp.WSGIApplication([
		('/', MainHandler),
        ('/counter', Counter),
		#('/[O|o]rganizers', OrganizersHandler),
	], debug=False)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
