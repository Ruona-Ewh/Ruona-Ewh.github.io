from flask import render_template, url_for, request, redirect, flash
from . import app, db, cache, limiter, qrcode
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_user, logout_user, login_required
from .models import User, Url
import random, string, io



def generate_short_url(length=6):
    characters = string.ascii_letters + string.digits
    short_url = "".join(random.choice(characters) for _ in range(length))
    url = Url.query.filter_by(short_url=short_url).first()
    if url:
            return Url.generate_short_url()
    return short_url


def generate_qr_code(url):
    image = qrcode.make(url)
    image_io = io.BytesIO()
    image.save(image_io, 'PNG')
    image_io.seek(0)
    return image_io



@app.route('/', methods=['GET', 'POST'])
@limiter.limit('10/minutes')
def index():
    if request.method == 'POST':
        original_url = request.form['original_url']
        short_url = request.form.get('custom_url', generate_short_url())
        existing_url = Url.query.filter_by(user_id=current_user.id).filter_by(original_url=original_url).first()

        if existing_url:
            flash('Custom URL already exists. Enter another one !')
            return redirect(url_for('index'))

        if not original_url:
            flash('The URL is required!')
            return redirect(url_for('index'))

        if not short_url:
            short_url = generate_short_url()

        url = Url(original_url=original_url, short_url=short_url, user_id=current_user.id)
        db.session.add(url)
        db.session.commit()
        short_url = request.host_url + short_url
        return render_template('index.html', short_url=short_url, url=url)

    return render_template('index.html', url=None)



@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route('/dashboard')
@login_required
def dashboard():
    urls = Url.query.filter_by(user_id=current_user.id).order_by(Url.date_created.desc()).all()
    host = request.host_url
    return render_template('dashboard.html', urls=urls, host=host)



@app.route('/<short_url>')
@login_required
@cache.cached(timeout=30)
def redirect_url(short_url):
    url = Url.query.filter_by(short_url=short_url).first()
    if url:
        url.visits += 1
        db.session.commit()
        return redirect(url.original_url)
    else:
        return "Invalid URL"
    


@app.route('/<short_url>/analytics')
@login_required
@cache.cached(timeout=30)
def analytics(short_url):
    url = Url.query.filter_by(short_url=short_url).first() 
    host = request.host_url
    if url:
        return render_template('analytics.html', url=url, host=host)
    else:
        return "URL not found"
   


@app.route('/<short_url>/edit', methods=['GET', 'POST'])
@login_required
def edit(short_url):
    url = Url.query.filter_by(user_id=current_user.id).filter_by(short_url=short_url).first()
    host = request.host_url
    if url:
        if request.method == 'POST':
            custom_url = request.form['custom_url']
            if custom_url:
                existing_url = Url.query.filter_by(custom_url=custom_url).first()
                if existing_url:
                    flash ('This custom URL already exists. Please try another one.')
                    return redirect(url_for('edit', short_url=short_url))
                url.custom_url = custom_url
                url.short_url = custom_url
            db.session.commit()
            return redirect(url_for('dashboard'))
        return render_template('edit.html', url=url, host=host)
    return 'URL not found.'
    


@app.route('/<short_url>/delete', methods=['GET'])
@login_required
def delete(short_url):
    url = Url.query.filter_by(user_id=current_user.id).filter_by(short_url=short_url).first()
    if url:
        db.session.delete(url)
        db.session.commit()
        return redirect(url_for('history'))
    return 'URL not found.'



@app.route('/<short_url>/qr_code')
@login_required
@cache.cached(timeout=30)
@limiter.limit('10/minutes')
def generate_qr_code_url(short_url):
    url = Url.query.filter_by(short_url=short_url).first()
    if url:
        img_io = generate_qr_code(request.host_url + url.short_url)
        return img_io.getvalue(), 200, {'Content-Type': 'image/png'}
    return 'URL not found.'

   

@app.route('/history')
@login_required
def history():
    urls = Url.query.filter_by(user_id=current_user.id).order_by(Url.date_created.desc()).all()
    host = request.host_url
    return render_template('history.html', urls=urls, host=host)



@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        user = User.query.filter_by(username=username).first()
        if user:
            flash('This username already exists.')
            return redirect(url_for('signup'))
    
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email is already registered.')
            return redirect(url_for('signup'))
        
        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('signup'))
    
        new_user = User(username=username,email=email, password=generate_password_hash(password))

        db.session.add(new_user)
        db.session.commit()
        
        flash('Signup successful!')
        return redirect(url_for('index'))
    
    return render_template('signup.html', title='signup')



@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        old_user = User.query.filter_by(email=email).first()
        if old_user:
            if check_password_hash(old_user.password, password):
                login_user(old_user)
                flash('Login Successful')
                return redirect(url_for('login'))
            
            if check_password_hash(old_user.password, password) == False:
                flash('Invalid username or password')
                return redirect(url_for('login'))
    
    return render_template('login.html', title='Login')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))

