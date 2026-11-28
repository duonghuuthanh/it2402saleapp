import math
from flask import render_template, request, redirect, flash
from eapp import app, dao, login
from flask_login import login_user, logout_user


@app.route('/')
def index():
    products = dao.load_products(kw=request.args.get('kw'),
                                 cate_id=request.args.get('category_id'),
                                 page=int(request.args.get('page', 1)))

    page_size = app.config['PAGE_SIZE']

    return render_template('index.html', products=products, pages=math.ceil(dao.count_products()/page_size))


@app.route('/login')
def login_view():
    return render_template('login.html')


@app.route('/login', methods=['post'])
def login_process():
    username = request.form.get('username')
    password = request.form.get('password')

    user = dao.authenticate(username, password)
    if user:
        login_user(user=user)
    else:
        flash('Thông tin đăng nhập không hợp lệ! Vui lòng kiểm tra lại', 'danger')

    next = request.args.get('next')
    if next:
        return redirect(next)

    return redirect('/admin')


@app.route('/logout')
def logout_process():
    logout_user()
    return redirect('/login')


@app.route('/register')
def register_view():
    return render_template('register.html')

@app.route('/register', methods=['post'])
def register_process():
    password = request.form.get('password')
    confirm = request.form.get('confirm')
    username = request.form.get('username')

    if not password or not confirm or password != confirm:
        flash('Mật khẩu không khớp!', 'danger')
    elif dao.check_existing_username(username) is not None:
        flash(f'{username} đã tồn tại!', 'danger')
    else:
        data = request.form.copy()
        del data['confirm']
        avatar = request.files.get('avatar')

        try:
            dao.add_user(**data, avatar=avatar)
        except Exception as ex:
            flash(f'Hệ thống bị lỗi, do {str(ex)}', 'danger')
        else:
            return redirect('/login')

    return redirect('/register')

@app.context_processor
def common_responses():
    return {
        'categories': dao.load_categories()
    }

@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


if __name__ == '__main__':
    with app.app_context():
        from eapp import admin
        app.run(debug=True)
