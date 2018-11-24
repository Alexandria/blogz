from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy


app  = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_ECHO']= True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:root@localhost:8889/blogz'
app.secret_key = '1234567oooooo'
db = SQLAlchemy(app)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True) 
    title = db.Column(db.String(50))
    content = db.Column(db.String(300))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, content, user_id):
        self.title = title
        self.content = content 
        self.user_id = user_id

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(120), unique = True) # This will make it so you cannont have multiple enties with the same email. 
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref = 'user_id')


    def __init__(self, email, password):
        self.email = email
        self.password = password


@app.route('/blog', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        new_subject = request.form.get('subject')
        new_text = request.form['text']
        list_blog = Blog(new_subject, new_text)
        db.session.add(list_blog)
        db.session.commit()
        return render_template('viewBlog.html', pagetitle = "New Blog", pageHeader = new_subject, show_text = new_text )
    
    # If the user selects a certain blog
    if request.args.get('id'):
        id = request.args.get('id')
        view = Blog.query.get(id)
        return render_template('viewBlog.html', pageTitle = 'Blog Entry '+id,  pageHeader = view.title, show_text = view.content )


    blog = Blog.query.all()
    return render_template('blog.html', pageTitle = 'Blog', blog = blog, pageHeader = 'View all')

  
    

@app.route('/newpost')
def addBlog():
    return render_template('addBlog.html', pageTitle = "Create Blog", pageHeader = 'Create a new blog')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email = email).first()
        
        if user and user.password == password:
            session['email'] = email
            return redirect('/blog')
        else:
            return '<h1>not the correct login</h1>'
        
    
    return render_template('login.html', pageHeader = "Log in")


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        new_usr = User(email, password)
        
        user = User.query.filter_by(email = email).first()
        if not user:
            db.session.add(new_usr)
            db.session.commit()
            session['email']=email
            return redirect('/blog')
        

    return render_template('register.html', pageHeader = "Register")


@app.route('/logout')
def logout():
    
    if 'email' not in  session:
        return '<h1>You are already logged out</h1>'

    del session['email']
    return redirect('/blog')    

if __name__ == '__main__':
    app.run()


