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
import re, languages, os

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from google.appengine.dist import use_library

use_library('django', '0.96')

from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp\
import util, template


def get_country(self):
    # country = urlfetch.fetch("http://geoip.wtanaka.com/cc/" + self.request.remote_addr).content
    return "en"


def isAddressValid(email):
    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
            return 1
    return 0


def get_device(self, info):
    uastring = self.request.user_agent
    if "Mobile" in uastring and "Safari" in uastring:
        kind = "mobile"
    else:
        kind = "desktop"

    if "MSIE" in uastring:
        browser = "Explorer"
    elif "Firefox" in uastring:
        browser = "Firefox"
    elif "Presto" in uastring:
        browser = "Opera"
    elif "Android" in uastring and "AppleWebKit" in uastring:
        browser = "Chrome for andriod"
    elif "iPhone" in uastring and "AppleWebKit" in uastring:
        browser = "Safari for iPhone"
    elif "iPod" in uastring and "AppleWebKit" in uastring:
        browser = "Safari for iPod"
    elif "iPad" in uastring and "AppleWebKit" in uastring:
        browser = "Safari for iPad"
        kind = "desktop"
    elif "Chrome" in uastring:
        browser = "Chrome"
    elif "AppleWebKit" in uastring:
        browser = "Safari"
    else:
        browser = "unknow"

    device = {
                 "kind": kind,
                 "browser": browser,
                 "uastring": uastring
             }[info]

    return device


def set_lang_cookie_and_return_dict(self):
    if self.request.get("hl") == "":
        # ask for cookie
        lang_cookie = self.request.cookies.get("hl")
        c = get_country(self)
        if not lang_cookie:
            if c == "ca" or c == "uk" or c == "us" or c == "eu" or c == "de"\
               or c == "gb" or c == "jp" or c == "cn" or c == "in" or c == "ru"\
               or c == "no" or c == "au" or c == "nz" or c == "se" or c == "dk":
                lang_cookie = "en"
            elif c == "br" or c == "pt":
                lang_cookie = "pt"
            else:
                lang_cookie = "es"
    else:
        lang_cookie = self.request.get("hl")

    if lang_cookie != "en" and lang_cookie != "es" and lang_cookie != "pt":
        lang_cookie = "en"

    self.response.headers.add_header("Set-Cookie", "hl=" + lang_cookie + ";")
    lang = {
               'en': languages.en,
               'es': languages.es,
               'pt': languages.pt
           }[lang_cookie]
    return lang


def set_version_device(self):
    if self.request.get("device") == "":
        version_device = self.request.cookies.get("device")
        if not version_device:
            version_device = get_device(self, 'kind') or "desktop"
    else:
        version_device = self.request.get("device")

    self.response.headers.add_header("Set-Cookie", "device=" + version_device + ";")

    return version_device


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


class MobileHandler(webapp.RequestHandler):
    def get(self):
        self.response.headers.add_header("Set-Cookie", "device=mobile;")
        self.redirect("http://m.startechconf.com")


class RedirectHandler(webapp.RequestHandler):
    def get(self):
        self.redirect("/")


class MainHandler(webapp.RequestHandler):
    def get(self):
        params = {
            'path': self.request.path,
            'lang': set_lang_cookie_and_return_dict(self),
        }
        self.response.out.write(
            template.render('index.html', params))

    def post(self):
        self.redirect("/")


class NextVersionHandler(webapp.RequestHandler):
    def get(self):
        params = {
            'path': self.request.path,
            'lang': set_lang_cookie_and_return_dict(self),
        }
        self.response.out.write(
            template.render('2013.html', params))

    def post(self):
        self.redirect("/")


class OrganizersHandler(webapp.RequestHandler):
    def get(self):
        params = {
            'path': self.request.path,
            'lang': set_lang_cookie_and_return_dict(self)
        }
        self.response.out.write(template.render('organizers.html', params))


class AssistantsHandler(webapp.RequestHandler):
    def get(self):
        params = {
            'path': self.request.path,
            'lang': set_lang_cookie_and_return_dict(self)
        }
        self.response.out.write(template.render('assistants.html', params))


class SponsorsHandler(webapp.RequestHandler):
    def get(self):
        params = {
            'path': self.request.path,
            'lang': set_lang_cookie_and_return_dict(self)
        }
        self.response.out.write(template.render('sponsors.html', params))


class ScheduleHandler(webapp.RequestHandler):
    def get(self):
        params = {
            'path': self.request.path,
            'lang': set_lang_cookie_and_return_dict(self)
        }
        self.response.out.write(template.render('schedule.html', params))


class Counter(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        language = self.request.headers["Accept-Language"]

        emailQuery = self.request.get("email")
        q = db.Query(Register).filter('email =', emailQuery)

        if q.count() >= 1:
            result = q.fetch(5)
            preregistered = emailQuery + ' <span style="color: green">is pre-registered</span><ul>'
            for p in result:
                preregistered += "<li><b>When:</b> " + p.when.strftime(
                    "%A, %B %d, %Y - %I:%M:%S %p %Z") + " | <b>Country:</b> " + str(p.country) + "</li>"
            preregistered += "</ul>"

        else:
            if emailQuery <> "":
                preregistered = emailQuery + ' <span style="color: red">is not pre-registered</span>'
            else:
                preregistered = ""

        if user:
            greeting = (
                "Welcome, %s <a href=\"%s\">sign out</a><h1 style=\"font-size: 2em;\">There are %s people pre-registered</h1><hr>Your country:  %s<hr>Your language: %s <hr><h1>Validator</h1>%s" %
                (user.nickname(), users.create_logout_url(self.request.path), str(we_are().count()), get_country(self),
                 language, preregistered))
        else:
            greeting = (
                "<a href=\"%s\">Sign in or register</a> to see the Counter <hr>Your country:  %s <hr>Your language: %s <hr><h1>Validator</h1>%s" %
                (users.create_login_url(self.request.path), get_country(self), language, preregistered))

        self.response.out.write("<html><body>%s</body></html>" %
                                (greeting))


def main():
    """
    Main
    """
    application = webapp.WSGIApplication([
                                             ('/', MainHandler),
                                             ('/call_for_collaborators_2013[/]?', NextVersionHandler),
                                             ('/counter', Counter),
                                             ('/team', OrganizersHandler),
                                             ('/assistants', AssistantsHandler),
                                             ('/sponsors', SponsorsHandler),
                                             ('/schedule', ScheduleHandler),
                                             ('/m', RedirectHandler),
                                             (r'/salir/', RedirectHandler),
                                             (r"/participa", RedirectHandler),
                                         ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
