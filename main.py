from webbrowser import get
from datetime import date,datetime
from flask import Flask, render_template, request, redirect, session

from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)
app.secret_key = "123"

conn_str = "mysql+pymysql://root:cset155@localhost/online_store"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()

def get_chat_data(uid):
    convo = conn.execute(text("""
        SELECT conversationid 
        FROM conversation
        WHERE customerid = :uid
        LIMIT 1
    """), {"uid": uid}).mappings().fetchone()

    if not convo:
        return None, []

    cid = convo['conversationid']

    messages = conn.execute(text("""
        SELECT * FROM message
        WHERE conversationid = :cid
        ORDER BY created_at ASC
    """), {"cid": cid}).mappings().fetchall()

    return cid, messages


@app.route('/')
def index():
    uid = session.get('user_id')

    messages = []
    convo_id = None

    if uid:
        convo_id, messages = get_chat_data(uid)

    
    discounted_products = conn.execute(text("""
        SELECT 
            p.productid,
            p.title,
            p.description,
            p.price AS original_price,
            d.discountprice,
            d.length
        FROM products p
        JOIN discount_products dp 
            ON p.productid = dp.productid
        JOIN discount d 
            ON d.discountid = dp.discountid
        WHERE d.length >= CURDATE()
    """)).mappings().all()

    return render_template('index.html', hot_deals=discounted_products, messages=messages,convo_id=convo_id,show_chat_popup=True)


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

            conn.execute(text("""
            INSERT INTO conversation (customerid)
            SELECT :uid
            WHERE NOT EXISTS (
                SELECT 1 FROM conversation WHERE customerid = :uid
            )
            """), {"uid": user.userid})

            conn.commit()
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

    if 'user_id' not in session:
        return redirect('/login')

    uid = session['user_id']
    messages = []
    convo_id = None
    if uid:
        convo_id, messages = get_chat_data(uid)
    # Fetch user info
    user = conn.execute(
        text("SELECT * FROM users WHERE userid = :uid"),
        {"uid": uid}
    ).mappings().fetchone()

    if not user:
        return redirect('/logout')

    # Fetch user's orders (JOIN cart → orders)
    userorders = conn.execute(
        text("""
            SELECT o.orderid, o.total, o.date, o.orderstatus
            FROM orders o
            JOIN cart c ON o.cartid = c.cartid
            WHERE c.userid = :uid
            ORDER BY o.date DESC
        """),
        {"uid": uid}
    ).mappings().fetchall()

    return render_template('account.html', user=user, orders=userorders,messages=messages,convo_id=convo_id,show_chat_popup=True)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/shop', methods=['GET', 'POST'])
def shop():

    q = request.args.get("q", "")

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

    uid = session.get('user_id')

    messages = []
    convo_id = None

    if uid:
            convo_id, messages = get_chat_data(uid)

    # 3. Handle POST actions
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        action = request.form.get('action')

        # (optional inputs from form)
        size = request.form.get('size')
        colorid = request.form.get('colorid')

        if not product_id:
            return redirect('/shop')

        if action == 'add':

            existing = conn.execute(text("""
                SELECT quantity FROM cartitem
                WHERE cartid = :cartid AND productid = :pid
            """), {
                "cartid": cartid,
                "pid": product_id
            }).fetchone()

            if existing:
                conn.execute(text("""
                    UPDATE cartitem
                    SET quantity = quantity + 1
                    WHERE cartid = :cartid AND productid = :pid
                """), {
                    "cartid": cartid,
                    "pid": product_id
                })
            else:
                conn.execute(text("""
                    INSERT INTO cartitem (cartid, productid, quantity)
                    VALUES (:cartid, :pid, 1)
                """), {
                    "cartid": cartid,
                    "pid": product_id
                })

        elif action == 'remove':
            conn.execute(text("""
                UPDATE cartitem
                SET quantity = quantity - 1
                WHERE cartid = :cartid AND productid = :pid
            """), {
                "cartid": cartid,
                "pid": product_id
            })

            conn.execute(text("""
                DELETE FROM cartitem
                WHERE cartid = :cartid
                AND productid = :pid
                AND quantity <= 0
            """), {
                "cartid": cartid,
                "pid": product_id
            })

        conn.commit()
        return redirect('/shop')


    # 4. GET request → load products
    if q:
        products = conn.execute(text("""
            SELECT 
                p.*,
                c.colorname,
                d.discountprice,
                d.length
            FROM products p
            LEFT JOIN color c ON p.colorid = c.colorid
            LEFT JOIN discount_products dp ON p.productid = dp.productid
            LEFT JOIN discount d ON dp.discountid = d.discountid
                AND CURRENT_DATE <= d.length
            WHERE p.title LIKE :q
            OR p.description LIKE :q
        """), {"q": f"%{q}%"}).fetchall()
    else:
        products = conn.execute(text("""
            SELECT 
                p.*,
                c.colorname,
                d.discountprice,
                d.length
            FROM products p
            LEFT JOIN color c ON p.colorid = c.colorid
            LEFT JOIN discount_products dp ON p.productid = dp.productid
            LEFT JOIN discount d ON dp.discountid = d.discountid
                AND CURRENT_DATE <= d.length
        """)).fetchall()

    colors = conn.execute(text("""
        SELECT colorid, colorname FROM color
    """)).fetchall()

    return render_template('shop.html', products=products, colors=colors,messages=messages,convo_id=convo_id,show_chat_popup=True)



@app.route('/cart', methods=['GET', 'POST'])
def cart():

     # 1. User must be logged in
    if 'user_id' not in session:
        return redirect('/signup')
    

    uid = session.get('user_id')
    messages = []
    convo_id = None

    if uid:
        convo_id, messages = get_chat_data(uid)

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

    return render_template("cart.html", cart_items=cart_items, cart_total=cart_total,messages=messages,convo_id=convo_id,show_chat_popup=True)




@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
    if not session.get('user_id'):
        return redirect('/signup')
    
    uid = session['user_id']
    messages = []
    convo_id = None

    if uid:
        convo_id, messages = get_chat_data(uid)
    
    if request.method == 'POST':
        name = session.get('username')
        comment = request.form['comment_box']
        rating = request.form['rating']
        userid = session.get('user_id')
        productid = request.form['productid']
        
        sql_check = text("""
        select productid from products where productid =:productid
        """)

        result= conn.execute(sql_check,{'productid':productid}).fetchone()

        if not result:
            return "invalid product"


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
    
    filter_by = request.args.get('filter_by', 'newest')

    
    base_sql = """
         select r.reviewid, r.reviewtext,r.rating,r.name,r.created_at,p.title as product_name from review r join products p on r.productid = p.productid
        """
    

    if filter_by == 'rating':
        base_sql += " order by r.rating desc"
    
    elif filter_by == 'oldest':
        base_sql += " order by r.created_at asc"
    
    else :
        base_sql += " order by r.created_at desc"
    sql = text(base_sql)
    
    result = conn.execute(sql).fetchall()

    return render_template('reviews.html',reviews = result,messages=messages,convo_id=convo_id,show_chat_popup=True)



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
    allwarranties = conn.execute(text("SELECT * FROM warranty")).fetchall()
    alldiscounts = conn.execute(text("SELECT * FROM discount")).fetchall()
    alldiscountproducts = conn.execute(text("SELECT * FROM discount_products")).fetchall()
    pending_returns = conn.execute(text("""
        SELECT * FROM returns
        WHERE status IN ('pending', 'pending_warranty', 'pending_expired')
        ORDER BY returnid DESC
    """)).fetchall()

    approved_returns = conn.execute(text("""
        SELECT * FROM returns
        WHERE status = 'approved'
        ORDER BY returnid DESC
    """)).fetchall()

    denied_returns = conn.execute(text("""
        SELECT * FROM returns
        WHERE status = 'denied'
        ORDER BY returnid DESC
    """)).fetchall()

    allconversations = conn.execute(text("""
        SELECT c.conversationid, c.customerid, u.username
        FROM conversation c
        JOIN users u ON c.customerid = u.userid
        ORDER BY c.created_at DESC
    """)).mappings().fetchall()


    return render_template(
        'admin.html',
        filter_section=filter_section,
        allusers=allusers,
        allproducts=allproducts,
        allorders=allorders,
        allreviews=allreviews,
        allwarranties=allwarranties,
        alldiscounts=alldiscounts,
        alldiscountproducts=alldiscountproducts,
        pending_returns=pending_returns,
        approved_returns=approved_returns,
        denied_returns=denied_returns,
        conversations=allconversations 
    )

@app.route('/admin/edit/<table>/<int:item_id>', methods=['GET', 'POST'])
def admin_edit(table, item_id):

    table_map = {
        "user": ("users", "userid"),
        "product": ("products", "productid"),
        "order": ("orders", "orderid"),
        "review": ("review", "reviewid"),
        "return": ("returns", "returnid"),
        "warranty": ("warranty", "warrantyid"),
        "discount": ("discount", "discountid"),
    }

    if table not in table_map:
        return render_template('admin.html', error="Invalid table")

    table_name, pk = table_map[table]

    # ---------------- GET ----------------
    if request.method == "GET":

        row = conn.execute(text(f"""
            SELECT * FROM {table_name}
            WHERE {pk} = :id
        """), {"id": item_id}).mappings().fetchone()

        if not row:
            return render_template('admin.html', error="Row not found")

        return render_template("adminedit.html", table=table, row=row)

    # ---------------- POST ----------------
    raw_data = dict(request.form)
    raw_data.pop('id', None)

    data = {}

    def parse_int(value):
        if value in (None, "", "None"):
            return None
        return int(value)

    def parse_float(value):
        if value in (None, "", "None"):
            return None
        return float(value)

    for key, value in raw_data.items():
        if key in ["price", "discountprice"]:
            data[key] = parse_float(value)
        elif key.endswith("id") or key in ["instock"]:
            data[key] = parse_int(value)
        else:
            data[key] = value

    if not data:
        return render_template('admin.html', error="No data provided")

    set_clause = ", ".join([f"{k} = :{k}" for k in data.keys()])
    data["id"] = item_id

    conn.execute(text(f"""
        UPDATE {table_name}
        SET {set_clause}
        WHERE {pk} = :id
    """), data)

    conn.commit()

    return redirect('/admin')

@app.route('/admin/edit/discount_product/<int:pid>/<int:did>', methods=['GET', 'POST'])
def edit_discount_product(pid, did):

    # ---------------- GET ----------------
    if request.method == "GET":

        row = conn.execute(text("""
            SELECT * FROM discount_products
            WHERE productid = :pid AND discountid = :did
        """), {
            "pid": pid,
            "did": did
        }).mappings().fetchone()

        if not row:
            return "Row not found", 404

        return render_template("adminedit.html", table="discount_product", row=row)

    # ---------------- POST ----------------
    data = dict(request.form)
    data.pop('productid', None)
    data.pop('discountid', None)

    if not data:
        return "No data provided", 400
    
    conn.execute(text("""
        UPDATE discount_products
        SET discountid = :new_discountid
        WHERE productid = :pid AND discountid = :did
    """), {
        "pid": pid,
        "did": did,
        "new_discountid": data.get("discountid", did)
    })

    conn.commit()

    return redirect('/admin')


@app.route('/admin/delete/discount_product/<int:pid>/<int:did>')
def delete_discount_product(pid, did):

    if 'role' not in session or session['role'] != 'admin':
        return redirect('/')

    conn.execute(text("""
        DELETE FROM discount_products
        WHERE productid = :pid AND discountid = :did
    """), {
        "pid": pid,
        "did": did
    })

    conn.commit()

    return redirect('/admin')
    



@app.route('/vendor', methods=['GET', 'POST'])
def vendor():

    if 'role' not in session or session['role'] != 'vendor':
        return redirect('/')

    products = conn.execute(text("""
        SELECT * FROM products
        WHERE vendorid = :vid
    """), {"vid": session['user_id']}).mappings().fetchall()

    orders = conn.execute(text("""
        SELECT DISTINCT
            o.orderid,
            o.total,
            o.date,
            o.orderstatus
        FROM orders o
        JOIN orderitems oi ON o.orderid = oi.orderid
        JOIN products p ON oi.productid = p.productid
        WHERE p.vendorid = :vid
        ORDER BY o.date DESC
    """), {"vid": session['user_id']}).mappings().fetchall()

    return render_template('vendor.html', products=products, orders=orders)


@app.route('/editprod/<int:pid>', methods=['GET'])
def editprod(pid):

    if 'role' not in session or session['role'] != 'vendor':
        return redirect('/')

    product = conn.execute(text("""
        SELECT * FROM products
        WHERE productid = :pid AND vendorid = :vid
    """), {"pid": pid, "vid": session['user_id']}).mappings().fetchone()

    colors = conn.execute(text("""
        SELECT colorid, colorname FROM color
    """)).fetchall()

    if not product:
        return "Product not found or not yours", 404

    return render_template('editprod.html', product=product, colors=colors)


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
            image = :image,
            colorid = :colorid
        WHERE productid = :pid AND vendorid = :vid
    """), {
        "title": request.form['title'],
        "description": request.form['description'],
        "price": request.form['price'],
        "instock": request.form['instock'],
        "size": request.form['size'],
        "warrantyid": request.form['warrantyid'],
        "image": request.form['image'],
        "colorid": request.form['colorid'],  # 👈 ADD THIS
        "pid": pid,
        "vid": session['user_id']
    })

    conn.commit()

    return redirect('/vendor')

@app.route('/addprod', methods=['GET'])
def addprod():

    if 'role' not in session or session['role'] != 'vendor':
        return redirect('/')

    return render_template("addprod.html")


@app.route('/addprod', methods=['POST'])
def saveprod():

    if 'role' not in session or session['role'] != 'vendor':
        return redirect('/')

    conn.execute(text("""
        INSERT INTO products 
        (title, description, price, instock, size, warrantyid, image, vendorid, colorid)
        VALUES (:title, :description, :price, :instock, :size, :warrantyid, :image, :vendorid, :colorid)
    """), {
        "title": request.form['title'],
        "description": request.form['description'],
        "price": request.form['price'],
        "instock": request.form['instock'],
        "size": request.form['size'],
        "warrantyid": request.form['warrantyid'],
        "image": request.form['image'],
        "vendorid": session['user_id'],
        "colorid": request.form['colorid']
    })

    conn.commit()
    return redirect('/vendor')


@app.route('/deleteprod/<int:pid>')
def deleteprod(pid):

    if 'role' not in session or session['role'] not in ['vendor', 'admin']:
        return redirect('/')

    conn.execute(text("DELETE FROM cartitem WHERE productid = :pid"), {"pid": pid})
    conn.execute(text("DELETE FROM orderitems WHERE productid = :pid"), {"pid": pid})
    conn.execute(text("DELETE FROM discount_products WHERE productid = :pid"), {"pid": pid})
    conn.execute(text("DELETE FROM review WHERE productid = :pid"), {"pid": pid})
    conn.execute(text("DELETE FROM wishlist WHERE productid = :pid"), {"pid": pid})

    conn.execute(text("""
        DELETE FROM products
        WHERE productid = :pid
    """), {"pid": pid})

    conn.commit()
    return redirect('/admin' if session['role'] == 'admin' else '/vendor')

@app.route('/admin/delete/user/<int:uid>')
def admin_delete_user(uid):
    if 'role' not in session or session['role'] != 'admin':
        return redirect('/')

    conn.execute(text("DELETE FROM users WHERE userid = :id"), {"id": uid})
    conn.commit()
    return redirect('/admin')


@app.route('/admin/delete/order/<int:oid>')
def admin_delete_order(oid):
    if 'role' not in session or session['role'] != 'admin':
        return redirect('/')

    conn.execute(text("DELETE FROM orders WHERE orderid = :id"), {"id": oid})
    conn.commit()
    return redirect('/admin')


@app.route('/admin/delete/review/<int:rid>')
def admin_delete_review(rid):
    if 'role' not in session or session['role'] != 'admin':
        return redirect('/')

    conn.execute(text("DELETE FROM review WHERE reviewid = :id"), {"id": rid})
    conn.commit()
    return redirect('/admin')


@app.route('/admin/delete/warranty/<int:wid>')
def admin_delete_warranty(wid):
    if 'role' not in session or session['role'] != 'admin':
        return redirect('/')

    conn.execute(text("DELETE FROM warranty WHERE warrantyid = :id"), {"id": wid})
    conn.commit()
    return redirect('/admin')


@app.route('/admin/delete/discount/<int:did>')
def admin_delete_discount(did):
    if 'role' not in session or session['role'] != 'admin':
        return redirect('/')

    conn.execute(text("DELETE FROM discount WHERE discountid = :id"), {"id": did})
    conn.commit()
    return redirect('/admin')

@app.route('/admin/link_discount', methods=['POST'])
def link_discount():
    if 'role' not in session or session['role'] != 'admin':
        return redirect('/')

    productid = request.form['productid']
    discountid = request.form['discountid']

    conn.execute(text("""
        INSERT INTO discount_products (productid, discountid)
        VALUES (:pid, :did)
    """), {
        "pid": productid,
        "did": discountid
    })

    conn.commit()
    return  redirect('/admin')

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():

    # Must be logged in
    if 'user_id' not in session:
        return redirect('/login')
    
    uid = session['user_id']
    messages = []
    convo_id = None

    if uid:
        convo_id, messages = get_chat_data(uid)

    cartid = session.get('cartid')

    # No cart → go back
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

    # Empty cart check
    if not cart_items:
        return redirect('/cart')

    # Calculate total
    total = sum(item.price * item.quantity for item in cart_items)

    # PLACE ORDER
    if request.method == 'POST':

        from datetime import date

        # 1. Create order
        conn.execute(text("""
            INSERT INTO orders (date, total, orderstatus, cartid)
            VALUES (:date, :total, :status, :cartid)
        """), {
            "date": date.today(),
            "total": total,
            "status": "pending",
            "cartid": cartid
        })

        # 2. Get new order ID safely
        order_id = conn.execute(
            text("SELECT LAST_INSERT_ID()")
        ).scalar()

        # 3. Insert order items + update stock
        for item in cart_items:

            # reduce stock
            conn.execute(text("""
                UPDATE products
                SET instock = instock - :qty
                WHERE productid = :pid
            """), {
                "qty": item.quantity,
                "pid": item.productid
            })

            # insert order item
            conn.execute(text("""
                INSERT INTO orderitems (orderid, productid, quantity, price)
                VALUES (:oid, :pid, :qty, :price)
            """), {
                "oid": order_id,
                "pid": item.productid,
                "qty": item.quantity,
                "price": item.price
            })

        # 4. Clear cart
        conn.execute(text("""
            DELETE FROM cartitem WHERE cartid = :cid
        """), {"cid": cartid})

        # 5. Reset session cart
        session.pop('cartid', None)

        # 6. Final commit
        conn.commit()

        # 7. Show success page
        return render_template(
            "checkoutfinal.html",
            total=total,
            order_id=order_id,
            messages=messages,
            convo_id=convo_id,
            show_chat_popup=True
        )
    
    return render_template('checkout.html', cart_items=cart_items, total=total)


@app.route('/warranty', methods=['GET', 'POST'])
def warranty():

    if 'user_id' not in session:
        return redirect('/login')
    uid = session['user_id']
    messages = []
    convo_id = None

    if uid:
        convo_id, messages = get_chat_data(uid)

    result = None
    status = None

    if request.method == 'POST':
        action = request.form.get('action')

        if action == "create":
                if 'role' not in session or session['role'] != 'admin':
                    return redirect('/')
     
                expire_date = datetime.strptime(
                request.form['expire_box'],
                "%m/%d/%Y"
                 ).date()
        
                conn.execute(text("""
                insert into warranty (expire_date) values (:expire_date)
                """),
                {'expire_date': expire_date}
                )

                conn.commit()
                return redirect('/warranty')
    
        elif action == "check":

            orderid = request.form['order_id']
            uid = session['user_id']

            result = conn.execute(text("""
            SELECT 
                p.title,
                w.expire_date
                FROM orders o
                JOIN cart c ON o.cartid = c.cartid
                JOIN orderitems oi ON o.orderid = oi.orderid
                JOIN products p ON oi.productid = p.productid
                LEFT JOIN warranty w ON p.warrantyid = w.warrantyid
                WHERE o.orderid = :oid
                AND c.userid = :uid
                LIMIT 1
            """), {
                "oid": orderid,
                "uid": uid
            }).mappings().fetchone()

            if result and result['expire_date']:
                if result['expire_date'] >= date.today():
                    status = "active"
                else:
                    status = "expired"
            else:
                status = "none"

    return render_template(
            "warranty.html",
            result=result,
            status=status,
            current_date=date.today(),
            messages=messages,
            convo_id=convo_id,
            show_chat_popup=True
        )


@app.route('/return', methods=['GET', 'POST'])
def returns():

    description = request.form.get("description", "")

    if 'user_id' not in session:
        return redirect('/login')

    uid = session['user_id']
    messages = []
    convo_id = None

    if uid:
        convo_id, messages = get_chat_data(uid)

    if request.method == 'POST':

        complaint = request.form['complaint']
        title = request.form['title']
        type_ = request.form['type']
        orderid = request.form['order_id']

        order_check = conn.execute(text("""
            SELECT o.orderid
            FROM orders o
            JOIN cart c ON o.cartid = c.cartid
            WHERE o.orderid = :oid
            AND c.userid = :uid
        """), {"oid": orderid, "uid": uid}).fetchone()

        if not order_check:
            return "Invalid order"

        warranty = conn.execute(text("""
            SELECT w.warrantyid, w.expire_date
            FROM orderitems oi
            JOIN products p ON oi.productid = p.productid
            LEFT JOIN warranty w ON p.warrantyid = w.warrantyid
            WHERE oi.orderid = :oid
            LIMIT 1
        """), {"oid": orderid}).mappings().fetchone()

        status = "pending"

        if warranty and warranty['expire_date']:
            if warranty['expire_date'] >= date.today():
                status = "pending_warranty"
            else:
                status = "pending_expired"

        conn.execute(text("""
            INSERT INTO returns (orderid, title, complaint, type, status, warrantyid)
            VALUES (:oid, :title, :complaint, :type, :status, :wid)
        """), {
            "oid": orderid,
            "title": title,
            "complaint": complaint,
            "type": type_,
            "status": status,
            "wid": warranty['warrantyid'] if warranty else None
        })

        conn.commit()

        return redirect('/return')

    user_returns = conn.execute(text("""
        SELECT returnid, title, complaint, type, status
        FROM returns
        WHERE orderid IN (
            SELECT o.orderid
            FROM orders o
            JOIN cart c ON o.cartid = c.cartid
            WHERE c.userid = :uid
        )
        ORDER BY returnid DESC
    """), {"uid": uid}).fetchall()

    return render_template("return.html", user_returns=user_returns,messages=messages,convo_id=convo_id,show_chat_popup=True)


@app.route('/return/approve/<int:rid>')
def approve_return(rid):

    if 'role' not in session or session['role'] != 'admin':
        return redirect('/')

    conn.execute(text("""
        UPDATE returns
        SET status = 'approved'
        WHERE returnid = :id
    """), {"id": rid})

    conn.commit()
    return redirect('/admin')

@app.route('/return/deny/<int:rid>')
def deny_return(rid):

    if 'role' not in session or session['role'] != 'admin':
        return redirect('/')

    conn.execute(text("""
        UPDATE returns
        SET status = 'denied'
        WHERE returnid = :id
    """), {"id": rid})

    conn.commit()
    return redirect('/admin')


@app.route('/admin/delete/return/<int:return_id>')
def delete_return(return_id):

    if 'role' not in session or session['role'] != 'admin':
        return redirect('/')

    conn.execute(text("""
        DELETE FROM returns
        WHERE returnid = :id
    """), {"id": return_id})

    conn.commit()

    return redirect('/admin')

@app.route('/admin/add_warranty', methods=['POST'])
def add_warranty():
    if 'role' not in session or session['role'] != 'admin':
        return redirect('/')

    expire_date = request.form['expire_date']

    conn.execute(text("""
        INSERT INTO warranty (expire_date)
        VALUES (:date)
    """), {"date": expire_date})

    conn.commit()
    return redirect('/admin')



@app.route('/admin/add_discount', methods=['POST'])
def add_discount():
    if 'role' not in session or session['role'] != 'admin':
        return redirect('/')

    conn.execute(text("""
        INSERT INTO discount (length, discountprice, price)
        VALUES (:length, :dp, :price)
    """), {
        "length": request.form['length'],
        "dp": request.form['discountprice'],
        "price": request.form['price']
    })

    conn.commit()
    return redirect('/admin')


@app.route('/discount',methods=['get','post'])
def create_discount():
    if 'role' not in session or session['role'] not in ['admin', 'vendor']: 
     return redirect('/')

    if request.method =='POST':

        end_date = request.form['end_date']
        disc_price = request.form['disc_price']
        og_price = request.form['og_price']
        product_id = request.form['product_id']

        conn.execute(text("""
        insert into discount (length,discountprice,price,productid)
        values (:end_date,:disc_price,:og_price,:product_id)
        """),{
            "end_date": end_date,
            "disc_price": disc_price,
            "og_price": og_price,
            "product_id": product_id
        }
        )

        conn.commit()
        return redirect('/discount')
    return render_template('discount.html')





@app.route("/chat")
def chat():
    if 'user_id' not in session:
        return redirect('/login')

    uid = session['user_id']
    messages = []
    convo_id = None

    convo = conn.execute(text("""
        SELECT * FROM conversation
        WHERE customerid = :uid
        AND type = 'admin'
        LIMIT 1
    """), {"uid": uid}).mappings().fetchone()

    if not convo:
        conn.execute(text("""
            INSERT INTO conversation (customerid, adminid, type)
            VALUES (:uid, :aid, 'admin')
        """), {"uid": uid,"aid":None})
        conn.commit()

        convo_id = conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()
    else:
        convo_id = convo['conversationid']

    messages = conn.execute(text("""
            select m.*,u.username as sender_name
            from message m
            join users u on m.senderid = u.userid
            where m.conversationid = :cid
            order by m.created_at asc
    """), {"cid": convo_id}).mappings().fetchall()

    return render_template("chat.html", messages=messages, convo_id=convo_id)



@app.route("/send_message", methods=['POST'])
def send_message():
    if 'user_id' not in session:
        return redirect('/login')

    uid = session['user_id']

    cid = request.form.get('conversationid')

    content = request.form.get('content',"")

    if not content:
        return redirect(request.referrer or '/')

    conn.execute(text("""
        INSERT INTO message (conversationid, senderid, content)
        VALUES (:cid, :sid, :content)
    """), {
        "cid": cid,
        "sid": uid,
        "content": content
    })

    conn.commit()

    return redirect(request.referrer or '/')


@app.route('/admin/chat/<int:cid>')
def admin_chat(cid):

    if session.get('role') != 'admin':
        return redirect('/')

    
    conn.execute(text("""
        UPDATE conversation
        SET adminid = :aid
        WHERE conversationid = :cid AND adminid IS NULL
    """), {
        "aid": session['user_id'],
        "cid": cid
    })
    conn.commit()

    conversations = conn.execute(text("""
        SELECT c.conversationid, u.username
        FROM conversation c
        JOIN users u ON c.customerid = u.userid
        ORDER BY c.conversationid DESC
    """)).mappings().fetchall()

    messages = conn.execute(text("""
            select m.*,u.username as sender_name
            from message m
            join users u on m.senderid = u.userid
            where m.conversationid = :cid
            order by m.created_at asc
    """), {"cid": cid}).mappings().fetchall()

    return render_template(
        "admin_chat.html",
        messages=messages,
        conversations=conversations,
        convo_id=cid
    )


@app.route('/admin/send_message', methods=['POST'])
def admin_send_message():
    if session.get('role') != 'admin':
        return redirect('/')

    cid = request.form['conversationid']

    convo = conn.execute(text("""
        SELECT * FROM conversation
        WHERE conversationid = :cid
    """), {"cid": cid}).fetchone()

    if not convo:
        return "Invalid conversation"

    conn.execute(text("""
        INSERT INTO message (conversationid, senderid, content)
        VALUES (:cid, :sid, :content)
    """), {
        "cid": cid,
        "sid": session['user_id'],
        "content": request.form['content']
    })

    conn.commit()

    return redirect(f"/admin/chat/{cid}")


@app.route('/vendor/chat/<int:cid>')
def vendor_chat(cid):

    if session.get('role') != 'vendor':
        return redirect('/')

    convo = conn.execute(text("""
        SELECT *
        FROM conversation
        WHERE conversationid = :cid
        AND vendorid = :vid
    """), {
        "cid": cid,
        "vid": session['user_id']
    }).mappings().fetchone()

    if not convo:
        return redirect('/')

    conversations = conn.execute(text("""
        SELECT
            c.conversationid,
            u.username
        FROM conversation c
        JOIN users u
            ON c.customerid = u.userid
        WHERE c.vendorid = :vid
        ORDER BY c.created_at ASC
    """), {
        "vid": session['user_id']
    }).mappings().fetchall()

    messages = conn.execute(text("""
        SELECT
            m.*,
            u.username AS sender_name
        FROM message m
        JOIN users u
            ON m.senderid = u.userid
        WHERE m.conversationid = :cid
        ORDER BY m.created_at ASC
    """), {
        "cid": cid
    }).mappings().fetchall()

    return render_template(
        'vendor_chat.html',
        messages=messages,
        conversations=conversations,
        convo_id=cid
    )

@app.route('/vendor/send_message', methods=['POST'])
def vendor_send_message():

    if session.get('role') != 'vendor':
        return redirect('/')

    cid = int(request.form['conversationid'])

    content = request.form.get('content', '').strip()

    if not content:
        return redirect(request.referrer or '/')

    convo = conn.execute(text("""
        SELECT *
        FROM conversation
        WHERE conversationid = :cid
        AND vendorid = :vid
    """), {
        "cid": cid,
        "vid": session['user_id']
    }).mappings().fetchone()

    if not convo:
        return redirect('/')

    conn.execute(text("""
        INSERT INTO message (
            conversationid,
            senderid,
            content
        )
        VALUES (
            :cid,
            :sid,
            :content
        )
    """), {
        "cid": cid,
        "sid": session['user_id'],
        "content": content
    })

    conn.commit()

    return redirect(f"/vendor/chat/{cid}")





@app.route('/vendor/inbox')
def vendor_inbox():

    if session.get('role') != 'vendor':
        return redirect('/')

    conversations = conn.execute(text("""
        SELECT
            c.conversationid,
            u.username
        FROM conversation c
        JOIN users u
            ON c.customerid = u.userid
        WHERE c.vendorid = :vid
        ORDER BY c.created_at ASC
    """), {
        "vid": session['user_id']
    }).mappings().fetchall()

    if not conversations:
        return "No conversations yet"

    return render_template("vendor_chat.html",
    conversations=conversations,messages=[],
    convo_id=None
    )


@app.route('/start_chat/<int:vendor_id>')
def start_chat(vendor_id):

    if 'user_id' not in session:
        return redirect('/login')

    uid = session['user_id']

    convo = conn.execute(text("""
        SELECT conversationid
        FROM conversation
        WHERE customerid = :uid
        AND vendorid = :vid
        LIMIT 1
    """), {
        "uid": uid,
        "vid": vendor_id
    }).mappings().fetchone()

    if not convo:
        conn.execute(text("""
            INSERT INTO conversation (customerid, vendorid)
            VALUES (:uid, :vid)
        """), {
            "uid": uid,
            "vid": vendor_id
        })
        conn.commit()

        cid = conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()
    else:
        cid = convo['conversationid']

    return redirect(f"/inbox/{cid}")



@app.route('/inbox/<int:cid>')
def inbox(cid):

    if 'user_id' not in session:
        return redirect('/login')

    uid = session['user_id']

    conversations = conn.execute(text("""
        SELECT c.conversationid, u.username
        FROM conversation c
        JOIN users u ON c.vendorid = u.userid
        WHERE c.customerid = :uid
        ORDER BY c.created_at DESC
    """), {"uid": uid}).mappings().fetchall()

    messages = conn.execute(text("""
        SELECT m.*, u.username AS sender_name
        FROM message m
        JOIN users u ON m.senderid = u.userid
        WHERE m.conversationid = :cid
        ORDER BY m.created_at ASC
    """), {"cid": cid}).mappings().fetchall()

    return render_template(
        "inbox.html",
        conversations=conversations,
        messages=messages,
        convo_id=cid,
        show_chat_popup=False
    )

@app.route('/my_inbox')
def my_inbox():

    if 'user_id' not in session:
        return redirect('/login')

    uid = session['user_id']

    convo = conn.execute(text("""
        SELECT conversationid
        FROM conversation
        WHERE customerid = :uid
        ORDER BY created_at DESC
        LIMIT 1
    """), {"uid": uid}).mappings().fetchone()

    if not convo:
        return "No conversations yet"

    return redirect(f"/inbox/{convo['conversationid']}")



@app.route('/admin/inbox')
def admin_inbox():

    if session.get('role') != 'admin':
        return redirect('/')

    convo = conn.execute(text("""
        SELECT conversationid
        FROM conversation
        ORDER BY conversationid DESC
        LIMIT 1
    """)).mappings().fetchone()

    if not convo:
        return "No conversations"

    return redirect(f"/admin/chat/{convo['conversationid']}")

if __name__ == '__main__':
    app.run(debug=True)