@app.route('/warranty', methods=['GET', 'POST'])
def warranty():

    if 'user_id' not in session:
        return redirect('/login')

    result = None
    status = None

    if request.method == 'POST':
        action = request.form.get('action')

        if action == "create":
                if 'role' not in session or session['role'] != 'admin':
                    return redirect('/')
     
                expire_date =request.form['expire_box']
        
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
            current_date=date.today()
        )