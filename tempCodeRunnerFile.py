@app.route('/shop', methods=['GET', 'POST'])
def shop():

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

            # NOTE: size/color are NOT stored yet in DB,
            # so they are currently ignored for cart logic

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
    products = conn.execute(text("""
        SELECT p.*, c.colorname,d.discountprice
        FROM products p
        LEFT JOIN color c ON p.colorid = c.colorid
        LEFT JOIN discount d ON p.productid = d.productid
        AND CURRENT_DATE <= d.length
    """)).fetchall()

    colors = conn.execute(text("""
        SELECT colorid, colorname FROM color
    """)).fetchall()

    return render_template('shop.html', products=products, colors=colors)