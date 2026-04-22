@app.route('/delete_return/<int:return_id>',methods =['POST'])
def delete_return(return_id):

    if 'user_id' not in session:
        return redirect('/login')
    
    uid = session['user_id']

    sql = text("""
        delete from returns where returnid = :id and user_id =:uid
    
    """)
    conn.execute(sql, {'id':return_id, 'uid':uid})
    conn.commit()

    return redirect ('/return')
