import webapp2, cgi, jinja2, os, re

import random, string, hashlib

from google.appengine.ext import db

#@template_dir: stores the folder in which we will be fetching the files
template_dir = os.path.join(os.path.dirname(__file__), 'templates')

#@jinja_env: sets environment for the web-page
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


def make_salt():
    ###returns random number of size 5
    return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw, key):
    ###encode the username and password with the key and returns the encoded form
    """if salt == None:
        salt = make_salt()"""
    h = hashlib.sha256(name + pw).hexdigest()
    return '%s:%s' % (key, h)

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    ###validate username
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    ###validate Password
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    ###Validate Email
    return not email or EMAIL_RE.match(email)

def valid_pw(name, pw, h):
    ###convert the username and passsword to hash code and compares with the h 
    ###if they patches returns true else return false
    list1 = h.split(':')
    hash = make_pw_hash(name, pw, list1[0])
    if h == hash:
        return True
    return False

class BaseHandler(webapp2.RequestHandler):
    ###Base Class controlling the rendering part of the page
    def write(self,*a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t =jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(BaseHandler):
    ###main page is launch when base URL is entered in browser
    def render_front(self, title="" , art="", error=""):
        ###Renders the form page
        self.render("form.html", title=title, art=art, error=error)
    
    def get(self):
        ###This funtion is called when the user calls MainPage with get method
        self.render_front()
        
    def post(self):
        ###This funtion is called when the user calls MainPage with post method
        title = self.request.get("title")
        art = self.request.get("art")

        if title and art:
            self.write("Thanks!")
        else:
            error = "we need both a title and some artwork!"
            seld.render_front(title,art,error)

class User(db.Model):
    ###Uesr table storing Username and Password
    username = db.StringProperty(required = True)
    password = db.StringProperty(required = True)

class SignUp(BaseHandler):
    ###SignUp page
    def render_front(self, **details):
        
        self.render("signup-form.html", **details)
        
    def get(self):
        self.render_front()

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")
        have_error = False

        params = dict(username = username, email = email)

        if not valid_username(username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif password != verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            p = User(username = username, password = password)
            p.put()
            self.response.headers.add_header('Set-Cookie', 'user_id=%s; Path=/'%(make_pw_hash(username, password, p.key().id())))
            self.redirect('/welcome')
            
            

class Welcome(BaseHandler):
    ###Welcome page
    def get(self):
        cookie = self.request.cookies.get('user_id')
        if cookie:
            list1 = cookie.split(':')
            key = db.Key.from_path('User', int(list1[0]))
            user = db.get(key)
            if valid_pw(user.username,user.password, cookie):
                self.write('Welcome %s'%(user.username))
            else:
                self.render('signup-form.html')
        else:
                self.render('signup-form.html')

class Logout(BaseHandler):
        ###logout page clears cookies and send user to signup page
        def get(self):
                #Clear Cookies
                self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
                self.redirect('/signup')

class Login(BaseHandler):
    ###Login Class handles user login
    def get(self):
        ###when Login page is called with get Method this function is called and 
        ###it Displays the login page
        self.render('login.html')
        
    def post(self):
        ###when Login page is called with post Method this function is called and 
        ###it valid's user and send it to welcome page.
        username = self.request.get("username")
        password = self.request.get("password")
        params = dict(username = username)
        u = User.all();
        u.filter('username = ', username)
        u.filter('password = ', password)
        if(u.count() > 0):
            u = u.get()
            self.response.headers.add_header('Set-Cookie', 'user_id=%s; Path=/'%(make_pw_hash(username, password, u.key().id())))
            self.redirect('/welcome')
        else:
            params['error_valid'] = 'Invalid login'
            self.render('login.html', **params)
        
application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/signup', SignUp),
    ('/welcome', Welcome),
    ('/login', Login),
    ('/logout', Logout),
], debug=True)

