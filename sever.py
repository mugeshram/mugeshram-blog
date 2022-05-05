from flask import Flask,render_template,url_for,request,redirect
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired,EqualTo,Email
from flask_ckeditor import CKEditorField,CKEditor
import sqlite3
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime as dt
from post import Post
from mail import Mailer

import  time
app = Flask(__name__)
app.secret_key = "5548"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ckeditor = CKEditor(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'http://127.0.0.1:5000/login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Blogpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=False, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    author_id = db.Column(db.Integer,db.ForeignKey("users.id"))
    comments = db.relationship('Comment', backref='comment_blog')

    def get_dic(self):
        dic = {}
        for column in self.__table__.columns:
            dic[column.name] = getattr(self, column.name)
        return dic


class Users(db.Model,UserMixin):
 id = db.Column(db.Integer,primary_key=True)
 username = db.Column(db.String(250),unique=False,nullable=False)
 email = db.Column(db.String(250),unique=True,nullable=False)
 password = db.Column(db.String(250),unique=False,nullable=False)
 blogs = db.relationship('Blogpost',backref='bloger')
 status = db.Column(db.String(30),unique=False,nullable=True)
 comments = db.relationship('Comment', backref='comment_author')



 def hash_password(self, password):
     self.password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

 def check_password(self, password):
     is_match = check_password_hash(self.password, password)
     return is_match



 def __repr__(self):
  return '<User %r>' % self.username


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(250), unique=False, nullable=False)
    blog_id = db.Column(db.Integer, db.ForeignKey("blogpost.id"))
    command_author_id=db.Column(db.Integer, db.ForeignKey("users.id"))
    date = db.Column(db.String(100), unique=False, nullable=True)


# db.create_all()
# db.session.commit()

class Signin_form(FlaskForm):
    user = StringField('Username')
    email = StringField('Email',validators=[DataRequired(message="input required"),Email(message="please put valid email")])
    password = PasswordField('Password',validators=[DataRequired(message="input required")])
    conform = PasswordField('Conform-password', validators=[DataRequired(message="input required"),EqualTo('password',message="passwords must math")])
    submit = SubmitField('Submit')

class Login_form(FlaskForm):
    email = StringField('Email',validators=[DataRequired(message="input required"),Email(message="please put valid email")])
    password = PasswordField('Password',validators=[DataRequired(message="input required")])
    submit = SubmitField('login')

class Comment_form(FlaskForm):
    body = CKEditorField('Comment', validators=[DataRequired(message="input required")])
    submit = SubmitField('Comment')


class Blog_form(FlaskForm):
    title = StringField('Blog Title',validators=[DataRequired(message="input required")])
    subtitle = StringField('Blog Subtitle', validators=[DataRequired(message="input required")])
    author = StringField('Blog Author', validators=[DataRequired(message="input required")])
    img_url = StringField('Blog Image Url', validators=[DataRequired(message="input required")])
    body = CKEditorField('Blog Body',validators=[DataRequired(message="input required")])
    submit = SubmitField('Submit blog')

class Edit_form(FlaskForm):
    title = StringField('Blog Title',validators=[DataRequired(message="input required")])
    subtitle = StringField('Blog Subtitle', validators=[DataRequired(message="input required")])
    author = StringField('Blog Author', validators=[DataRequired(message="input required")])
    img_url = StringField('Blog Image Url', validators=[DataRequired(message="input required")])
    body = CKEditorField('Blog Body',validators=[DataRequired(message="input required")])
    submit = SubmitField('Submit blog')

blocker = Post()
mail = Mailer()
mail.to_gmail = "mugeshkrish007@gmail.com"
@app.route('/')
def home():
    admin = False
    user_id = current_user.get_id()
    if user_id != None:
        user = Users.query.get(int(user_id))
        if user_id == '1' or user.status == 'bloger':
            admin = True
    blocks = db.session.query(Blogpost).all()
    head_detail = {
        'head':"Mugesh's block",
        'sub':"A collection of stories."
    }
    return render_template("index.html", image="https://images.unsplash.com/photo-1570215171655-49dc3fa810b2?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1170&q=80", heading=head_detail, blocks=blocks,admin=admin,current_user=current_user)

@app.route('/about')
def about():
    head_detail = {
        'head': "About",
        'sub': "This is what i do."
    }
    return render_template("about.html", image=url_for('static',filename='about-bg.jpg'), heading=head_detail,current_user=current_user)

@app.route('/contact')
def contact():
    head_detail = {
        'head': "Contact",
        'sub': "Have questions?i have answers."
    }
    return render_template("contact.html", image=url_for('static',filename='contact-bg.jpg'), heading=head_detail,current_user=current_user)

@app.route('/post/<int:id>',)
def post(id):
    admin = False
    user_id = current_user.get_id()
    block = Blogpost.query.get(id)
    comments = block.comments

    comments = [(comment,Users.query.get(comment.command_author_id)) for comment in comments]
    if user_id != None:
        if user_id == '1' or block.author_id == int(user_id):
            admin = True

    form = Comment_form()
    head_detail = {
        'head': block.title,
        'sub': block.subtitle
    }
    return render_template("post.html", image=block.img_url,heading=head_detail ,block=block ,form=form,admin=admin,current_user=current_user,comments=comments)

@app.route('/contact/send', methods=['POST'])
def send():
    message=f"Subject:Block-request\n\nName:{request.form['name']}\nEmail:{request.form['email']}\nPhonenumber:{request.form['phonenumber']}\n\n{request.form['text']}"
    mail.send(message)
    head_detail = {
        'head': "Sending Successful",
        'sub': "You will be answered."
    }
    return render_template("contact.html", image=url_for('static',filename='contact-bg.jpg'), heading=head_detail,current_user=current_user)




@app.route('/newblog',methods=['GET','POST'])
def newblog():
    date = dt.now()
    formated_date = f"{date.strftime('%B')} {date.day}, {date.year}"
    form = Blog_form()
    user_id = int(current_user.get_id())

    head_detail = {
        'head': "New Blog",
        'sub': "Create knowledgeable world."
    }
    head_url="https://images.unsplash.com/photo-1529854140025-25995121f16f?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1170&q=80"
    if form.validate_on_submit():
        new = Blogpost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            author=form.author.data,
            img_url=form.img_url.data,
            body=form.body.data,
            date=formated_date,
            author_id = user_id


        )
        db.session.add(new)
        db.session.commit()
        return redirect(url_for('home'))


    return render_template('newblog.html', image=head_url, heading=head_detail, form=form,current_user=current_user)

@app.route('/editblog/<int:id>',methods=['GET','POST'])
def editblog(id):
    form = Edit_form()
    head_url = "https://images.unsplash.com/photo-1529854140025-25995121f16f?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1170&q=80"
    head_detail = {
        'head': "Edit Blog",
        'sub': "Create knowledgeable world."
    }
    if form.validate_on_submit():
        block = Blogpost.query.get(id)
        block.title = form.title.data
        block.subtitle = form.subtitle.data
        block.author = form.author.data
        block.img_url = form.img_url.data
        block.body = form.body.data
        db.session.commit()
        return redirect(url_for('home'))

    block = Blogpost.query.get(id)
    form.title.data = block.title
    form.subtitle.data = block.subtitle
    form.author.data = block.author
    form.img_url.data = block.img_url
    form.body.data = block.body


    return render_template('editblog.html', image=head_url, heading=head_detail, form=form,id=id,current_user=current_user)

@app.route('/delete/<int:id>',methods=['POST','GET'])
def deleteblog(id):
    block = Blogpost.query.get(id)
    db.session.delete(block)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/signin', methods=['POST','GET'])
def signin():
    form = Signin_form()
    error = ""
    if form.validate_on_submit():
        try:
            new = Users(username=form.user.data, email=form.email.data)
            password = form.password.data
            new.hash_password(password)
            db.session.add(new)
            db.session.commit()

        except:
            error = "email already exist"
            form.password.data = ""
            form.conform.data = ""
        else:

            return redirect(url_for('login'))

    return render_template('signin.html', form=form, error = error)


@app.route('/login', methods=['POST','GET'])
def login():
    form = Login_form()
    error = ""
    if form.validate_on_submit():
        data = Users.query.filter_by(email=form.email.data).first()
        if data == None  :
            error = "invalid email/password"
        else:
            if data.check_password(form.password.data) :
                login_user(data)
                next = request.args.get('next')
                print(next)
                if next :
                    return redirect(next)
                return redirect(url_for('home'))
            else:
                error = "invalid email/password"


    return render_template('login.html',form=form,error=error)

@app.route('/comment/<int:id>', methods=['POST','GET'])
@login_required
def comment(id):
    date = dt.now()
    formated_date = f"{date.strftime('%B')} {date.day}, {date.year}"
    form = Comment_form()
    user_id = int(current_user.get_id())
    if form.validate_on_submit():
        new = Comment(comment=form.body.data, blog_id=id,command_author_id=user_id,date=formated_date)
        db.session.add(new)
        db.session.commit()
        form.body.data = ""
    return redirect(url_for('post', id=id))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))



if __name__ == "__main__":
    app.run(debug=True)