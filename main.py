from flask import Flask, request, redirect, render_template, url_for, session
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'a;lsdkj1adoij'


db.create_all()
class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text())
    author = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, author):
        self.title = name
        self.body = body
        self.author = author


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='author')
    

    def __init__(self, email, password):
        self.email = email
        self.password = password


def validate_form(username, password, verify_password):
    existing_user = User.query.filter_by(username = username).first()

    if username == "":
        username_error = "A username is required to continue."
    elif " " in username:
        username_error = "The username cannot contain any spaces."
    elif len(username)<3 or len(username)>20:
        username_error = "The username should be between 3 and 20 characters."
    elif username == existing_user.username:
        username_error = "Username already exists"

    if password == "" or password == None:
        password_error = "A password is required to continue."
    elif " " in password:
        password_error = "The password cannot contain any spaces."
    elif len(password)<3 or len(password)>20:
        password_error = "The password should be between 3 and 20 characters."

    if password != verify_password:
        verify_password_error = "The passwords do not match."
    
    #https://www.tutorialspoint.com/python/python_tuples.htm - accessing elements of tuples
    return (username_error, password_error, verify_password_error)


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup' 'blog', '/blog/<blog_id>', '/blog/<int:blog_id>', '/blog/ALL', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect('/blog')


@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    username_error = ""
    password_error = ""
    verify_password_error = ""
    

    if request.method == "POST":
        username = request.form['username']
        password= request.form['password']
        verify_password = request.form['verify_password']
        error_msgs = validate_form(username, password, verify_password)
        if '' not in error_msgs:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username']=username
            return render_template('addblog', title="Add a Blog")
        else:
            redirect('/signup')
            
    else: 
        return render_template('signup.html')


@app.route('/login', methods =['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
    
        if username == "" or password == "":
            if username == "":
                username_error = 'Please enter your username'
            
            if password == "":
                password_error = 'Please enter your password'
            
            return render_template('login.html')
            
        user = User.query.filter_by(username=username, password=password).first()
        if not user:
            username_error = 'Username not found'
            return render_template('login.html')
        
        if user.password != password:
            password_error = "Incorrect Password"
            return render_template('login.html')
        
        if user and user.password == password:
            status = "Currently Logged In"
            return redirect('/newpost')
            
    
        current_user = User.query.filter_by(email=email.first())
        session['username'] = current_user.username
        return render_template('addblog', title='Add a Blog', username=username)
    
    return render_template('login.html')
    

@app.route('/blog', defaults={'blog_id' : 'All'}) #http://flask.pocoo.org/docs/1.0/api/#url-route-registrations
@app.route('/blog/<blog_id>')
@app.route('/blog/<int:blog_id>')
def blog(blog_id):
    if blog_id != 'All':
        blog = Blog.query.get(int(blog_id))
        return render_template('singlepost.html',title=blog.title,blog=blog)
    
    blogs = Blog.query.all()
    return render_template('blogs.html',title="Blogz", blogs=blogs)

        
@app.route('/user_blogs', methods=['POST']) #http://flask.pocoo.org/docs/1.0/api/#url-route-registrations
def user_blogs(user_id, blog_id):
    if request.method == 'POST':
        if blog_id != 'All':
            blog = Blog.query.get(int(blog_id))
            return render_template('singlepost.html',title=blog.title,blog=blog)
    
        blogs = Blog.query.filter_by(username=username).all()
        user = User.query.filter_by(username=username).first()
        return render_template('user_blogs.html',title="Blogz", blogs=blogs, username=username)  

@app.route('/addblog')
def addblog():
    return render_template('addblog.html',title="Add a Blog")

@app.route('/newpost', methods=['POST'])
def new_post():

    owner = User.query.filter_by(username = session['username']).first()

    blog_title = request.form['title']
    blog_body = request.form['body']
    body_error = ""
    title_error = ""

    if blog_title == "":
        title_error = "Give your blog a title"
    if blog_body == "":
        body_error = "Tell us something"
    if body_error != "" or title_error != "":
        return render_template("addblog.html",title="Build-a-Blog",body_error=body_error,title_error=title_error,blog_title=blog_title,blog_body=blog_body)

    new_blog = Blog(blog_title, blog_body, author)
    db.session.add(new_blog)
    db.session.commit()
    blog = Blog.query.get(new_blog.id)
    return render_template('singlepost.html',title=blog.title,blog=blog)
    
@app.route('/logout', methods = ['POST'])
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/delete-blog', methods=['POST'])
def delete_blog():

    blog_id = int(request.form['blog-id'])
    blog = Blog.query.get(blog_id)
    db.session.delete(blog)
    db.session.commit()

    return redirect('/blog')


if __name__ == '__main__':
    app.run()