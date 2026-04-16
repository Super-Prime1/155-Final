from flask import Flask, render_template, request, redirect, session
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash,check_password_hash

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
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        sql = text("SELECT * FROM users WHERE username = :username")
        user = conn.execute(sql, {'username': username}).fetchone()

        if user and check_password_hash(user.password, password):

            session['user_id'] = user.userid
            session['username'] = user.username
            session['role'] = user.role

            print(session.get('user_id'))

            return redirect('/account')

        else:
            return render_template('signup.html', error="Invalid login")

    return render_template('signup.html') 


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


@app.route('/account', methods=['GET', 'POST'])
def account():
    return render_template('account.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/shop', methods=['GET', 'POST'])
def shop():

    # 1. User must be logged in
    if 'user_id' not in session:
        return redirect('/')

    # 2. Create a cart if the user doesn't have one yet
    if 'cartid' not in session:
        result = conn.execute(text("""
            INSERT INTO cart (userid)
            VALUES (:uid)
        """), {"uid": session['user_id']})
        conn.commit()
        session['cartid'] = result.lastrowid

    # 3. Now it's safe to read cartid
    cartid = session['cartid']

    if request.method == 'POST':
        product_id = request.form['product_id']
        action = request.form['action']

        if action == 'add':
            existing = conn.execute(text("""
                SELECT quantity FROM cartitem
                WHERE cartid = :cartid AND productid = :pid
            """), {"cartid": cartid, "pid": product_id}).fetchone()

            if existing:
                conn.execute(text("""
                    UPDATE cartitem
                    SET quantity = quantity + 1
                    WHERE cartid = :cartid AND productid = :pid
                """), {"cartid": cartid, "pid": product_id})
            else:
                conn.execute(text("""
                    INSERT INTO cartitem (cartid, productid, quantity)
                    VALUES (:cartid, :pid, 1)
                """), {"cartid": cartid, "pid": product_id})

            conn.commit()

        elif action == 'remove':
            conn.execute(text("""
                UPDATE cartitem
                SET quantity = quantity - 1
                WHERE cartid = :cartid AND productid = :pid
            """), {"cartid": cartid, "pid": product_id})

            conn.execute(text("""
                DELETE FROM cartitem
                WHERE cartid = :cartid AND productid = :pid AND quantity <= 0
            """), {"cartid": cartid, "pid": product_id})

            conn.commit()

        return redirect('/shop')

    products = conn.execute(text("SELECT * FROM products")).fetchall()
    return render_template('shop.html', products=products)



@app.route('/cart', methods=['GET', 'POST'])
def cart():

    # 1. User must be logged in
    if 'user_id' not in session:
        return redirect('/signup')

    # 2. Ensure cart exists
    if 'cartid' not in session:
        result = conn.execute(text("""
            INSERT INTO cart (userid)
            VALUES (:uid)
        """), {"uid": session['user_id']})
        conn.commit()
        session['cartid'] = result.lastrowid

    cartid = session['cartid']
    if request.method == 'POST':
        action = request.form['action']

        if action == 'add_one':
            product_id = request.form['product_id']
            conn.execute(text("""
                UPDATE cartitem
                SET quantity = quantity + 1
                WHERE cartid = :cartid AND productid = :pid
            """), {"cartid": session['cartid'], "pid": product_id})

        elif action == 'remove_one':
            cartitemid = request.form['cartitemid']
            conn.execute(text("""
                UPDATE cartitem
                SET quantity = quantity - 1
                WHERE cartitemid = :cid
            """), {"cid": cartitemid})

            conn.execute(text("""
                DELETE FROM cartitem
                WHERE quantity <= 0
            """))

        elif action == 'remove_all':
            cartitemid = request.form['cartitemid']
            conn.execute(text("""
                DELETE FROM cartitem
                WHERE cartitemid = :cid
            """), {"cid": cartitemid})

        return redirect('/cart')

    # GET request → load cart
    cart_items = conn.execute(text("""
        SELECT c.cartitemid, c.productid, c.quantity,
               p.title, p.price
        FROM cartitem c
        JOIN products p ON c.productid = p.productid
        WHERE c.cartid = :cartid
    """), {"cartid": session['cartid']}).fetchall()

    cart_total = sum(item.price * item.quantity for item in cart_items)

    return render_template("cart.html", cart_items=cart_items, cart_total=cart_total)




@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
    if not session.get('user_id'):
        return redirect('/signup')
    
    if request.method == 'POST':
        name = session.get('username')
        comment = request.form['comment_box']
        rating = request.form['rating']
        userid = session.get('user_id')
        productid = 21
        sql = text("""
        insert into review (productid, userid, name, reviewtext, rating)
        values(:productid, :userid, :name, :reviewtext, :rating)
        """)

        conn.execute(sql,{
            'productid':productid,
            'userid':userid,
            'name':name,
            'reviewtext':comment,
            'rating':rating
        })

        conn.commit()
        return redirect('/reviews')
    
    sql = text('select * from review')
    result = conn.execute(sql).fetchall()

    return render_template('reviews.html',reviews = result)



@app.route('/delete_review/<int:review_id>', methods=['POST'])
def review_delete(review_id):
    sql = text("delete from review where reviewid = :id")
    conn.execute(sql,{'id' : review_id})
    conn.commit()

    return redirect('/reviews')

@app.route('/debug')
def debug():
    return str(session)



if __name__ == '__main__':
    app.run(debug=True)
