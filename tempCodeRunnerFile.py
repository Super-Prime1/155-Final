@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
    if 'username' not in session:
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