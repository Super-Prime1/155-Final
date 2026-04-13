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
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')

@app.route('/account', methods=['GET', 'POST'])
def account():
    return render_template('account.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')


@app.route('/shop', methods=['GET', 'POST'])
def shop():
    if request.method == 'POST':
        product_id = request.form['product_id']
        action = request.form['action']
        cartid = session['cartid']

        if action == 'add':
            # Check if item already in cart
            existing = conn.execute(text("""
                SELECT quantity FROM cartitem
                WHERE cartid = :cartid AND productid = :pid
            """), {"cartid": cartid, "pid": product_id}).fetchone()

            if existing:
                # Increase quantity
                conn.execute(text("""
                    UPDATE cartitem
                    SET quantity = quantity + 1
                    WHERE cartid = :cartid AND productid = :pid
                """), {"cartid": cartid, "pid": product_id})
            else:
                # Insert new cart item
                conn.execute(text("""
                    INSERT INTO cartitem (cartid, productid, quantity)
                    VALUES (:cartid, :pid, 1)
                """), {"cartid": cartid, "pid": product_id})

        elif action == 'remove':
            # Reduce quantity
            conn.execute(text("""
                UPDATE cartitem
                SET quantity = quantity - 1
                WHERE cartid = :cartid AND productid = :pid
            """), {"cartid": cartid, "pid": product_id})

            # Delete if quantity hits 0
            conn.execute(text("""
                DELETE FROM cartitem
                WHERE cartid = :cartid AND productid = :pid AND quantity <= 0
            """), {"cartid": cartid, "pid": product_id})

        return redirect('/shop')

    # GET request → show products
    products = conn.execute(text("SELECT * FROM products")).fetchall()
    return render_template('shop.html', products=products)



@app.route('/cart', methods=['GET', 'POST'])
def cart():
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


if __name__ == '__main__':
    app.run(debug=True)
