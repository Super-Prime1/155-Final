@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
    if not session.get('user_id'):
        return redirect('/signup')
    
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
    
    sql = text("""
         select r.reviewid, r.reviewtext,r.rating,r.name,r.created_at,p.title as product_name from review r join products p on r.productid = p.productid
        """)
    result = conn.execute(sql).fetchall()

    return render_template('reviews.html',reviews = result)