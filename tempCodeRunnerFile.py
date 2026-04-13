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

    