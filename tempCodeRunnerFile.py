@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        sql = text("SELECT * FROM users WHERE username = :username")
        user = conn.execute(sql, {'username': username}).fetchone()

        if user and check_password_hash(user.password, password):

            session['user_id'] = user.userid
            session['username'] = user.username
            session['role'] = user.role

            return redirect('/dashboard')

        else:
            return render_template('login.html', error="Invalid login")

    return render_template('login.html') 
from flask import Flask, render_template, request, redirect, session
from sqlalchemy import create_engine, text

app = Flask(__name__)
app.secret_key = "123"

conn_str = "mysql+pymysql://root:cset155@localhost/online_store"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():    
    render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']

        check_sql = text("SELECT * FROM users WHERE email = :email OR username = :username")
        existing_user = conn.execute(check_sql, {
            'email': email,
            'username': username
        }).fetchone()

        if existing_user:
            return "User already exists"

        sql = text("""
            INSERT INTO users (name, email, username, password, role)
            VALUES (:name, :email, :username, :password, :role)
        """)

        conn.execute(sql, {
            'name': name,
            'email': email,
            'username': username,
            'password': password,
            'role': role
        })

        conn.commit()
        return redirect('/signup')

    return render_template('signup.html')
    render_template('signup.html')


@app.route('/account', methods=['GET', 'POST'])
def account():
    render_template('account.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/shop', methods=['GET', 'POST'])
def shop():
    conn.execute(text("SELECT * FROM products"))
    return render_template('shop.html')


if __name__ == '__main__':
    app.run(debug=True)

    
