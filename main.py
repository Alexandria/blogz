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

    def __init__(self, title, content, user):
        self.title = title
        self.content = content 
        self.user = user

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), unique = True) # This will make it so you cannont have multiple enties with the same username. 
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref = 'user')


    def __init__(self, username, password):
        self.username = username
        self.password = password



@app.route('/blog', methods = ['POST', 'GET'])
def index():
    user = User.query.filter_by(username = session['username']).first()

    if request.method == 'POST':
        new_subject = request.form.get('subject')
        new_text = request.form['text']
        
        list_blog = Blog(new_subject, new_text, user)
        db.session.add(list_blog)
        db.session.commit()
        return render_template('viewBlog.html', pagetitle = "New Blog", pageHeader = new_subject, show_text = new_text )
    
    # If the user selects a certain blog
    if request.args.get('id'):
        id = request.args.get('id')
        view = Blog.query.get(id)
        return render_template('viewBlog.html', pageTitle = 'Blog Entry '+id,  pageHeader = view.title, show_text = view.content )

    
    blog = Blog.query.all()
    if request.args.get('user'):
        user = request.args.get('user')
        user_blog = User.query.filter_by(username = user).first()
        user_id = user_blog.id
        blog = Blog.query.filter_by(user_id = user_id).all()
        return render_template('blog.html', pagetitle = 'My Blog', blog = blog)

    
    
    return render_template('blog.html', pagetitle = 'My Blog', blog = blog)
  
    
@app.route('/newpost')
def addBlog():
    if 'username' not in session:
        return redirect('/login')
    return render_template('addBlog.html', pageTitle = "Create Blog", pageHeader = 'Create a new blog')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username = username).first()
        
        if user and user.password == password:
            session['username'] = username
            return redirect('/blog')
        else:
            return '<h1>not the correct login</h1>'
        
    
    return render_template('login.html', pageHeader = "Log in")


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        new_usr = User(username, password)
        
        user = User.query.filter_by(username = username).first()
        if not user:
            db.session.add(new_usr)
            db.session.commit()
            session['username']=username
            return redirect('/blog')
        

    return render_template('register.html', pageHeader = "Register")


@app.route('/logout')
def logout():
    
    if 'username' not in  session:
        return '<h1>You are already logged out</h1>'

    del session['username']
    return redirect('/blog')   


if __name__ == '__main__':
    app.run()


