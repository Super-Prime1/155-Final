
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
        show_chat_popup=True
    )