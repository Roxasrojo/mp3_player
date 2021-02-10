import sqlite3

def create_table():
    conn=sqlite3.connect("player.db")
    cur=conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS playlist (id INTEGER PRIMARY KEY, path VARCHAR(150), file VARCHAR(100))")
    conn.commit()
    conn.close()

def delete_table():
    conn=sqlite3.connect("player.db")
    cur=conn.cursor()
    cur.execute("DROP TABLE playlist")
    conn.commit()
    conn.close()

def insert(path, file):
    conn=sqlite3.connect("player.db")
    cur=conn.cursor()
    cur.execute("INSERT INTO playlist (path, file) VALUES (?, ?)",(path, file))
    conn.commit()
    conn.close()

def view():
    conn=sqlite3.connect("player.db")
    cur=conn.cursor()
    cur.execute("SELECT file FROM playlist")
    rows=cur.fetchall()
    conn.close()
    return rows

def search(id):
    conn=sqlite3.connect("player.db")
    cur=conn.cursor()
    cur.execute("SELECT * FROM playlist WHERE id=?",(id,))
    rows=cur.fetchall()
    conn.close()
    return rows

def curr_song(file):
    conn=sqlite3.connect("player.db")
    cur=conn.cursor()
    cur.execute("SELECT * FROM playlist WHERE file=?",(file,))
    rows=cur.fetchall()
    conn.close()
    return rows

def delete_row(id):
    conn=sqlite3.connect("player.db")
    cur=conn.cursor()
    cur.execute("DELETE FROM playlist WHERE id=?",(id,))
    conn.commit()
    conn.close()

def update_id(id):
    conn=sqlite3.connect("player.db")
    cur=conn.cursor()
    for change in range(id, len(view())-1):
        next_id = change + 1
        cur.execute("UPDATE playlist SET id = ? WHERE id=?",(change,next_id))
        conn.commit()
    conn.close()

create_table()
