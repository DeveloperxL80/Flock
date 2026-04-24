from flask import Flask,render_template,request,redirect
import sqlite3
app=Flask(__name__)
def init_db():
 conn=sqlite3.connect("users.db")
 conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY,name TEXT,email TEXT,password TEXT,dob TEXT)")
 conn.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY,name TEXT,content TEXT)")
 conn.execute("CREATE TABLE IF NOT EXISTS pokes (id INTEGER PRIMARY KEY,post_id INTEGER)")
 conn.commit()
 conn.close()
@app.route("/")
def home():
 return render_template("register.html")
@app.route("/register",methods=["POST"])
def register():
 name=request.form["name"]
 email=request.form["email"]
 password=request.form["password"]
 dob=request.form["dob"]
 conn=sqlite3.connect("users.db")
 conn.execute("INSERT INTO users (name,email,password,dob) VALUES (?,?,?,?)",(name,email,password,dob))
 conn.commit()
 conn.close()
 return "Welcome "+name
@app.route("/login")
def login():
 return render_template("login.html")
@app.route("/login",methods=["POST"])
def login_post():
 email=request.form["email"]
 password=request.form["password"]
 conn=sqlite3.connect("users.db")
 user=conn.execute("SELECT * FROM users WHERE email=? AND password=?",(email,password)).fetchone()
 conn.close()
 if user:
  return redirect("/profile/"+str(user[0]))
 else:
  return "Wrong email or password!"
@app.route("/profile/<int:user_id>")
def profile(user_id):
 conn=sqlite3.connect("users.db")
 user=conn.execute("SELECT * FROM users WHERE id=?",(user_id,)).fetchone()
 posts=conn.execute("SELECT * FROM posts WHERE name=?",(user[1],)).fetchall()
 conn.close()
 return render_template("profile.html",user=user,posts=posts)
@app.route("/newpost")
def newpost():
 return render_template("newpost.html")
@app.route("/newpost",methods=["POST"])
def post_submit():
 content=request.form["content"]
 conn=sqlite3.connect("users.db")
 conn.execute("INSERT INTO posts (content) VALUES (?)",(content,))
 conn.commit()
 posts=conn.execute("SELECT posts.id,posts.name,posts.content,COUNT(pokes.id) FROM posts LEFT JOIN pokes ON posts.id=pokes.post_id GROUP BY posts.id").fetchall()
 conn.close()
 return render_template("feed.html",posts=posts)
@app.route("/feed")
def feed():
 conn=sqlite3.connect("users.db")
 posts=conn.execute("SELECT posts.id,posts.name,posts.content,COUNT(pokes.id) FROM posts LEFT JOIN pokes ON posts.id=pokes.post_id GROUP BY posts.id").fetchall()
 conn.close()
 return render_template("feed.html",posts=posts)
@app.route("/poke/<int:post_id>")
def poke(post_id):
 conn=sqlite3.connect("users.db")
 conn.execute("INSERT INTO pokes (post_id) VALUES (?)",(post_id,))
 conn.commit()
 conn.close()
 return redirect("/feed")
init_db()
if __name__=="__main__":
 app.run(host="0.0.0.0",port=5000)
