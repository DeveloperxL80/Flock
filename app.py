from flask import Flask,render_template,request,redirect
import sqlite3
app=Flask(__name__)
def init_db():
 conn=sqlite3.connect("users.db")
 conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY,name TEXT,email TEXT,password TEXT,dob TEXT,bio TEXT)")
 conn.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY,name TEXT,content TEXT)")
 conn.execute("CREATE TABLE IF NOT EXISTS pokes (id INTEGER PRIMARY KEY,post_id INTEGER)")
 conn.execute("CREATE TABLE IF NOT EXISTS supports (id INTEGER PRIMARY KEY,follower_id INTEGER,following_id INTEGER)")
 conn.execute("CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY,post_id INTEGER,name TEXT,content TEXT)")
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
 supporters=conn.execute("SELECT COUNT(*) FROM supports WHERE following_id=?",(user_id,)).fetchone()[0]
 conn.close()
 return render_template("profile.html",user=user,posts=posts,supporters=supporters)
@app.route("/support/<int:user_id>/<int:current_id>")
def support(user_id,current_id):
 conn=sqlite3.connect("users.db")
 existing=conn.execute("SELECT * FROM supports WHERE follower_id=? AND following_id=?",(current_id,user_id)).fetchone()
 if not existing:
  conn.execute("INSERT INTO supports (follower_id,following_id) VALUES (?,?)",(current_id,user_id))
  conn.commit()
 conn.close()
 return redirect("/profile/"+str(user_id))
@app.route("/update_bio/<int:user_id>",methods=["POST"])
def update_bio(user_id):
 bio=request.form["bio"]
 conn=sqlite3.connect("users.db")
 conn.execute("UPDATE users SET bio=? WHERE id=?",(bio,user_id))
 conn.commit()
 conn.close()
 return redirect("/profile/"+str(user_id))
@app.route("/newpost")
def newpost():
 return render_template("newpost.html")
@app.route("/newpost",methods=["POST"])
def post_submit():
 content=request.form["content"]
 conn=sqlite3.connect("users.db")
 conn.execute("INSERT INTO posts (content) VALUES (?)",(content,))
 conn.commit()
 raw=conn.execute("SELECT posts.id,posts.name,posts.content,COUNT(pokes.id) FROM posts LEFT JOIN pokes ON posts.id=pokes.post_id GROUP BY posts.id").fetchall()
 posts=[]
 for p in raw:
  comments=conn.execute("SELECT * FROM comments WHERE post_id=?",(p[0],)).fetchall()
  posts.append((p[0],p[1],p[2],p[3],comments))
 conn.close()
 return render_template("feed.html",posts=posts)
@app.route("/feed")
def feed():
 conn=sqlite3.connect("users.db")
 raw=conn.execute("SELECT posts.id,posts.name,posts.content,COUNT(pokes.id) FROM posts LEFT JOIN pokes ON posts.id=pokes.post_id GROUP BY posts.id").fetchall()
 posts=[]
 for p in raw:
  comments=conn.execute("SELECT * FROM comments WHERE post_id=?",(p[0],)).fetchall()
  posts.append((p[0],p[1],p[2],p[3],comments))
 conn.close()
 return render_template("feed.html",posts=posts)
@app.route("/poke/<int:post_id>")
def poke(post_id):
 conn=sqlite3.connect("users.db")
 conn.execute("INSERT INTO pokes (post_id) VALUES (?)",(post_id,))
 conn.commit()
 conn.close()
 return redirect("/feed")
@app.route("/comment/<int:post_id>",methods=["POST"])
def comment(post_id):
 content=request.form["content"]
 name=request.form["name"]
 conn=sqlite3.connect("users.db")
 conn.execute("INSERT INTO comments (post_id,name,content) VALUES (?,?,?)",(post_id,name,content))
 conn.commit()
 conn.close()
 return redirect("/feed")
@app.route("/search")
def search():
 query=request.args.get("q","")
 conn=sqlite3.connect("users.db")
 users=conn.execute("SELECT * FROM users WHERE name LIKE ?",(("%"+query+"%"),)).fetchall()
 posts=conn.execute("SELECT * FROM posts WHERE content LIKE ?",(("%"+query+"%"),)).fetchall()
 conn.close()
 return render_template("search.html",users=users,posts=posts,query=query)
init_db()
if __name__=="__main__":
 app.run(host="0.0.0.0",port=5000)
