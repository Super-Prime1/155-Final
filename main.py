from webbrowser import get

from flask import Flask, render_template, request, redirect, session
from psutil import users
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

        # Insert new user
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

        # New cart for user
        new_user_id = conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()

        conn.execute(text("""
            INSERT INTO cart (userid)
            VALUES (:uid)
        """), {"uid": new_user_id})
        conn.commit()

        return redirect('/signup')

    return render_template('signup.html')


@app.route('/account', methods=['GET', 'POST'])
def account():

    # User must be logged in
    if 'user_id' not in session:
        return redirect('/login')

    # Fetch the user's info
    user = conn.execute(text("""
        SELECT * FROM users WHERE userid = :uid
    """), {"uid": session['user_id']}).mappings().fetchone()

    # If somehow no user is found (rare but safe)
    if not user:
        return redirect('/logout')

    return render_template('account.html', user=user)


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




@app.route('/admin')
def admin():
    if 'role' not in session or session['role'] != 'admin':
        return redirect('/')

    filter_section = request.args.get('section', 'all')

    allusers = conn.execute(text("SELECT * FROM users")).fetchall()
    allproducts = conn.execute(text("SELECT * FROM products")).fetchall()
    allorders = conn.execute(text("SELECT * FROM orders")).fetchall()
    allreviews = conn.execute(text("SELECT * FROM review")).fetchall()
    allreturns = conn.execute(text("SELECT * FROM returns")).fetchall()
    allwarranties = conn.execute(text("SELECT * FROM warranty")).fetchall()
    alldiscounts = conn.execute(text("SELECT * FROM discount")).fetchall()

    return render_template(
        'admin.html',
        filter_section=filter_section,
        allusers=allusers,
        allproducts=allproducts,
        allorders=allorders,
        allreviews=allreviews,
        allreturns=allreturns,
        allwarranties=allwarranties,
        alldiscounts=alldiscounts
    )

@app.route('/admin/edit/<table>/<int:item_id>', methods=['GET'])
def admin_edit(table, item_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect('/')

    table_map = {
        "user": ("users", "userid"),
        "product": ("products", "productid"),
        "order": ("orders", "orderid"),
        "review": ("review", "reviewid"),
        "return": ("returns", "returnid"),
        "warranty": ("warranty", "warrantyid"),
        "discount": ("discount", "discountid")
    }

    table_name, pk = table_map[table]

    result = conn.execute(
        text(f"SELECT * FROM {table_name} WHERE {pk} = :id"),
        {"id": item_id}
    )

    row = result.mappings().fetchone()

    return render_template("adminedit.html", table=table, row=row)


@app.route('/admin/edit/<table>/<int:item_id>', methods=['POST'])
def admin_edit_post(table, item_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect('/')

    data = dict(request.form)

    table_map = {
        "user": ("users", "userid"),
        "product": ("products", "productid"),
        "order": ("orders", "orderid"),
        "review": ("review", "reviewid"),
        "return": ("returns", "returnid"),
        "warranty": ("warranty", "warrantyid"),
        "discount": ("discount", "discountid")
    }

    table_name, pk = table_map[table]

    set_clause = ", ".join([f"{key} = :{key}" for key in data.keys()])
    data["id"] = item_id

    conn.execute(
        text(f"UPDATE {table_name} SET {set_clause} WHERE {pk} = :id"),
        data
    )
    conn.commit()

    return redirect('/admin')


@app.route('/vendor', methods=['GET', 'POST'])
def vendor():

    # Only vendors can access this page
    if 'role' not in session or session['role'] != 'vendor':
        return redirect('/')

    # Fetch all products owned by this vendor
    products = conn.execute(text("""
        SELECT * FROM products
        WHERE vendorid = :vid
    """), {"vid": session['user_id']}).mappings().fetchall()

    return render_template('vendor.html', products=products)


@app.route('/editprod/<int:pid>', methods=['GET'])
def editprod(pid):

    if 'role' not in session or session['role'] != 'vendor':
        return redirect('/')

    product = conn.execute(text("""
        SELECT * FROM products
        WHERE productid = :pid AND vendorid = :vid
    """), {"pid": pid, "vid": session['user_id']}).mappings().fetchone()

    if not product:
        return "Product not found or not yours", 404

    return render_template('editprod.html', product=product)

@app.route('/editprod/<int:pid>', methods=['POST'])
def updateprod(pid):

    if 'role' not in session or session['role'] != 'vendor':
        return redirect('/')

    conn.execute(text("""
        UPDATE products
        SET title = :title,
            description = :description,
            price = :price,
            instock = :instock,
            size = :size,
            warrantyid = :warrantyid,
            image = :image
        WHERE productid = :pid AND vendorid = :vid
    """), {
        "title": request.form['title'],
        "description": request.form['description'],
        "price": request.form['price'],
        "instock": request.form['instock'],
        "size": request.form['size'],
        "warrantyid": request.form['warrantyid'],
        "image": request.form['image'],
        "pid": pid,
        "vid": session['user_id']
    })

    conn.commit()

    return redirect('/vendor')

@app.route('/addprod', methods=['GET'])
def addprod():

    if 'role' not in session or session['role'] != 'vendor':
        return redirect('/')

    return render_template('addprod.html')

@app.route('/addprod', methods=['POST'])
def saveprod():

    if 'role' not in session or session['role'] != 'vendor':
        return redirect('/')

    conn.execute(text("""
        INSERT INTO products (title, description, price, instock, size, warrantyid, image, vendorid)
        VALUES (:title, :description, :price, :instock, :size, :warrantyid, :image, :vendorid)
    """), {
        "title": request.form['title'],
        "description": request.form['description'],
        "price": request.form['price'],
        "instock": request.form['instock'],
        "size": request.form['size'],
        "warrantyid": request.form['warrantyid'],
        "image": request.form['image'],
        "vendorid": session['user_id']
    })

    conn.commit()
    return redirect('/vendor')


@app.route('/deleteprod/<int:pid>')
def deleteprod(pid):

    if 'role' not in session or session['role'] != 'vendor':
        return redirect('/')

    # Delete from dependent tables first
    conn.execute(text("DELETE FROM cartitem WHERE productid = :pid"), {"pid": pid})
    conn.execute(text("DELETE FROM orderitems WHERE productid = :pid"), {"pid": pid})
    conn.execute(text("DELETE FROM discount_products WHERE productid = :pid"), {"pid": pid})
    conn.execute(text("DELETE FROM color WHERE productid = :pid"), {"pid": pid})
    conn.execute(text("DELETE FROM review WHERE productid = :pid"), {"pid": pid})
    conn.execute(text("DELETE FROM wishlist WHERE productid = :pid"), {"pid": pid})

    # Now delete the product
    conn.execute(text("""
        DELETE FROM products
        WHERE productid = :pid AND vendorid = :vid
    """), {"pid": pid, "vid": session['user_id']})

    conn.commit()
    return redirect('/vendor')


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():

    if 'user_id' not in session:
        return redirect('/login')

    cartid = session.get('cartid')

    if not cartid:
        return redirect('/cart')

    # Get cart items
    cart_items = conn.execute(text("""
        SELECT c.cartitemid, c.quantity,
               p.productid, p.title, p.price
        FROM cartitem c
        JOIN products p ON c.productid = p.productid
        WHERE c.cartid = :cid
    """), {"cid": cartid}).mappings().fetchall()

    if not cart_items:
        return "Cart is empty"

    # Calculate total
    total = sum(item.price * item.quantity for item in cart_items)

    if request.method == 'POST':

        from datetime import date

        # Insert into orders
        result = conn.execute(text("""
            INSERT INTO orders (date, total, orderstatus, cartid)
            VALUES (:date, :total, :status, :cartid)
        """), {
            "date": date.today(),
            "total": total,
            "status": "pending",
            "cartid": cartid
        })
        conn.commit()

        # Get new order ID
        order_id = result.lastrowid

        # Insert into orderitems
        for item in cart_items:
            conn.execute(text("""
                INSERT INTO orderitems (orderid, productid, quantity, price)
                VALUES (:oid, :pid, :qty, :price)
            """), {
                "oid": order_id,
                "pid": item.productid,
                "qty": item.quantity,
                "price": item.price
            })

        # Clear cart
        conn.execute(text("""
            DELETE FROM cartitem WHERE cartid = :cid
        """), {"cid": cartid})

        conn.commit()

        return render_template("checkoutfinal.html", total=total, order_id=order_id)

    return render_template('checkout.html', cart_items=cart_items, total=total)

if __name__ == '__main__':
    app.run(debug=True)
