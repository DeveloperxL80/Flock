from flask import Flask,render_template,request,redirect,session
import psycopg2
import os
app=Flask(__name__)
app.secret_key="flock_secret_123"
ADMIN_PASSWORD="infoempty.gg"
DATABASE_URL=os.environ.get("DATABASE_URL")
def get_db():
 conn=psycopg2.connect(DATABASE_URL)
 return conn
def init_db():
 conn=get_db()
 cur=conn.cursor()
 cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY,name TEXT,email TEXT,password TEXT,dob TEXT,bio TEXT)")
 cur.execute("CREATE TABLE IF NOT EXISTS posts (id SERIAL PRIMARY KEY,name TEXT,content TEXT)")
 cur.execute("CREATE TABLE IF NOT EXISTS pokes (id SERIAL PRIMARY KEY,post_id INTEGER)")
 cur.execute("CREATE TABLE IF NOT EXISTS supports (id SERIAL PRIMARY KEY,follower_id INTEGER,following_id INTEGER)")
 cur.execute("CREATE TABLE IF NOT EXISTS comments (id SERIAL PRIMARY KEY,post_id INTEGER,name TEXT,content TEXT)")
 conn.commit()
 cur.close()
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
 conn=get_db()
 cur=conn.cursor()
 cur.execute("SELECT * FROM users WHERE email=%s",(email,))
 existing=cur.fetchone()
 if existing:
  cur.close()
  conn.close()
  return "This email is already registered!"
 cur.execute("INSERT INTO users (name,email,password,dob) VALUES (%s,%s,%s,%s)",(name,email,password,dob))
 conn.commit()
 cur.close()
 conn.close()
 return redirect("/login")
@app.route("/login")
def login():
 return render_template("login.html")
@app.route("/login",methods=["POST"])
def login_post():
 email=request.form["email"]
 password=request.form["password"]
 conn=get_db()
 cur=conn.cursor()
 cur.execute("SELECT * FROM users WHERE email=%s AND password=%s",(email,password))
 user=cur.fetchone()
 cur.close()
 conn.close()
 if user:
  session["user_id"]=user[0]
  session["user_name"]=user[1]
  return redirect("/feed")
 else:
  return "Wrong email or password!"
@app.route("/logout")
def logout():
 session.clear()
 return redirect("/login")
@app.route("/admin",methods=["GET","POST"])
def admin():
 if request.method=="POST":
  if request.form["password"]==ADMIN_PASSWORD:
   session["is_admin"]=True
   return redirect("/admin")
  else:
   return "Wrong admin password!"
 if not session.get("is_admin"):
  return render_template("admin_login.html")
 conn=get_db()
 cur=conn.cursor()
 cur.execute("SELECT * FROM users")
 users=cur.fetchall()
 cur.execute("SELECT * FROM posts")
 posts=cur.fetchall()
 cur.execute("SELECT COUNT(*) FROM comments")
 total_comments=cur.fetchone()[0]
 cur.close()
 conn.close()
 return render_template("admin.html",users=users,posts=posts,total_users=len(users),total_posts=len(posts),total_comments=total_comments)
@app.route("/admin/delete_user/<int:user_id>")
def delete_user(user_id):
 if not session.get("is_admin"):
  return redirect("/admin")
 conn=get_db()
 cur=conn.cursor()
 cur.execute("DELETE FROM users WHERE id=%s",(user_id,))
 conn.commit()
 cur.close()
 conn.close()
 return redirect("/admin")
@app.route("/admin/delete_post/<int:post_id>")
def delete_post(post_id):
 if not session.get("is_admin"):
  return redirect("/admin")
 conn=get_db()
 cur=conn.cursor()
 cur.execute("DELETE FROM posts WHERE id=%s",(post_id,))
 conn.commit()
 cur.close()
 conn.close()
 return redirect("/admin")
@app.route("/profile")
def profile():
 if "user_id" not in session:
  return redirect("/login")
 conn=get_db()
 cur=conn.cursor()
 cur.execute("SELECT * FROM users WHERE id=%s",(session["user_id"],))
 user=cur.fetchone()
 cur.execute("SELECT * FROM posts WHERE name=%s",(user[1],))
 posts=cur.fetchall()
 cur.execute("SELECT COUNT(*) FROM supports WHERE following_id=%s",(session["user_id"],))
 supporters=cur.fetchone()[0]
 cur.close()
 conn.close()
 return render_template("profile.html",user=user,posts=posts,supporters=supporters)
@app.route("/profile/<int:user_id>")
def profile_view(user_id):
 conn=get_db()
 cur=conn.cursor()
 cur.execute("SELECT * FROM users WHERE id=%s",(user_id,))
 user=cur.fetchone()
 cur.execute("SELECT * FROM posts WHERE name=%s",(user[1],))
 posts=cur.fetchall()
 cur.execute("SELECT COUNT(*) FROM supports WHERE following_id=%s",(user_id,))
 supporters=cur.fetchone()[0]
 cur.close()
 conn.close()
 return render_template("profile.html",user=user,posts=posts,supporters=supporters)
@app.route("/support/<int:user_id>")
def support(user_id):
 if "user_id" not in session:
  return redirect("/login")
 conn=get_db()
 cur=conn.cursor()
 cur.execute("SELECT * FROM supports WHERE follower_id=%s AND following_id=%s",(session["user_id"],user_id))
 existing=cur.fetchone()
 if not existing:
  cur.execute("INSERT INTO supports (follower_id,following_id) VALUES (%s,%s)",(session["user_id"],user_id))
  conn.commit()
 cur.close()
 conn.close()
 return redirect("/profile/"+str(user_id))
@app.route("/update_bio",methods=["POST"])
def update_bio():
 if "user_id" not in session:
  return redirect("/login")
 bio=request.form["bio"]
 conn=get_db()
 cur=conn.cursor()
 cur.execute("UPDATE users SET bio=%s WHERE id=%s",(bio,session["user_id"]))
 conn.commit()
 cur.close()
 conn.close()
 return redirect("/profile")
@app.route("/newpost")
def newpost():
 if "user_id" not in session:
  return redirect("/login")
 return render_template("newpost.html")
@app.route("/newpost",methods=["POST"])
def post_submit():
 if "user_id" not in session:
  return redirect("/login")
 content=request.form["content"]
 conn=get_db()
 cur=conn.cursor()
 cur.execute("INSERT INTO posts (name,content) VALUES (%s,%s)",(session["user_name"],content))
 conn.commit()
 cur.close()
 conn.close()
 return redirect("/feed")
@app.route("/feed")
def feed():
 if "user_id" not in session:
  return redirect("/login")
 conn=get_db()
 cur=conn.cursor()
 cur.execute("SELECT posts.id,posts.name,posts.content,COUNT(pokes.id) FROM posts LEFT JOIN pokes ON posts.id=pokes.post_id GROUP BY posts.id")
 raw=cur.fetchall()
 posts=[]
 for p in raw:
  cur.execute("SELECT * FROM comments WHERE post_id=%s",(p[0],))
  comments=cur.fetchall()
  posts.append((p[0],p[1],p[2],p[3],comments))
 cur.close()
 conn.close()
 return render_template("feed.html",posts=posts)
@app.route("/poke/<int:post_id>")
def poke(post_id):
 if "user_id" not in session:
  return redirect("/login")
 conn=get_db()
 cur=conn.cursor()
 cur.execute("INSERT INTO pokes (post_id) VALUES (%s)",(post_id,))
 conn.commit()
 cur.close()
 conn.close()
 return redirect("/feed")
@app.route("/comment/<int:post_id>",methods=["POST"])
def comment(post_id):
 if "user_id" not in session:
  return redirect("/login")
 content=request.form["content"]
 conn=get_db()
 cur=conn.cursor()
 cur.execute("INSERT INTO comments (post_id,name,content) VALUES (%s,%s,%s)",(post_id,session["user_name"],content))
 conn.commit()
 cur.close()
 conn.close()
 return redirect("/feed")
@app.route("/search")
def search():
 if "user_id" not in session:
  return redirect("/login")
 query=request.args.get("q","")
 conn=get_db()
 cur=conn.cursor()
 cur.execute("SELECT * FROM users WHERE name LIKE %s",("%"+query+"%",))
 users=cur.fetchall()
 cur.execute("SELECT * FROM posts WHERE content LIKE %s",("%"+query+"%",))
 posts=cur.fetchall()
 cur.close()
 conn.close()
 return render_template("search.html",users=users,posts=posts,query=query)
init_db()
if __name__=="__main__":
 app.run(host="0.0.0.0",port=5000)
