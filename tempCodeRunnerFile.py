@app.route("/chat")
def chat():
    if 'user_id' not in session:
        return redirect('/login')

    uid = session['user_id']
    messages = []
    convo_id = None

    if uid:
        convo_id, messages = get_chat_data(uid)

    convo = conn.execute(text("""
        SELECT * FROM conversation
        WHERE customerid = :uid
        LIMIT 1
    """), {"uid": uid}).mappings().fetchone()

    if not convo:
        conn.execute(text("""
            INSERT INTO conversation (customerid)
            VALUES (:uid)
        """), {"uid": uid})
        conn.commit()

        convo_id = conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()
    else:
        convo_id = convo['conversationid']

    messages = conn.execute(text("""
            select m.*,u.username
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

    convo = conn.execute(text("""
        SELECT conversationid 
        FROM conversation
        WHERE customerid = :uid
        LIMIT 1
    """), {"uid": uid}).mappings().fetchone()

    if not convo:
        return "No conversation found"

    cid = convo['conversationid']

    content = request.form['content']

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
            select m.*,u.username
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



if __name__ == '__main__':
    app.run(debug=True)