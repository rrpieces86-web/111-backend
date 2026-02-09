from flask import Flask, jsonify, request, render_template
import sqlite3

app = Flask(__name__)

DB_NAME = "budget_manager.db"

def init_db():
    conn = sqlite3.connect(DB_NAME) #opens a connection to the database
    cursor = conn.cursor() # creates a cursor or tool that let us send commands

    # users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      email TEXT UNIQUE,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      password TEXT NOT NULL DEFAULT ''                              
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT,
      description TEXT NOT NULL,
      amount REAL NOT NULL,
      date TEXT NOT NULL,
      category TEXT NOT NULL,
      user_id INT,
      FOREIGN KEY(user_id) REFERENCES users(id)
    )
""")

    conn.commit()#save changes to the  database
    conn.close() # close the connection to the database

@app.get("/api/health")
def health_check():
    return jsonify({"status": "OK"}), 200

@app.post("/api/register")
def register():
    data = request.get_json()
    print(data)
    user = data.get("name")
    email = data.get("email")
    password = data.get("password")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (user, email, password))
    conn.commit()
    conn.close()

    return jsonify({"message":"User registered successfully"}), 201

@app.get("/api/users")
def get_users():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # allow columns to be retrieved by name (e.g. row["name"])
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM users")
    rows = cursor.fetchall()
    print(rows)
    conn.close()

    users = []
    for row in rows:
        user = {"id":row["id"], "name":row["name"]}
        users.append(user)

    return jsonify({
        "success":True,
        "message":"Users retrieved successfully",
        "data":users

    }), 200

@app.get("/api/users/<int:user_id>")
def get_user_by_id(user_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    #validate if the user exist
    cursor.execute("SELECT id, name FROM users WHERE id=?", (user_id,))
    row  = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({
            "success":False,
            "message":"user not found"
        }), 404
    
    print(row["name"])
    conn.close()

    return jsonify({
        "success":True,
        "message":"user retrieved successfully",
        "data": {"id":row["id"], "name":row["name"]}
    }), 200

@app.delete("/api/users/<int:user_id>")
def delete_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    #validate if user exists
    cursor.execute("SELECT id, name FROM users WHERE id=?", (user_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({
            "success":False,
            "message":"user not found"
        }), 404
    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

    return jsonify({
        "success":True,
        "message":"user deleted successfully"
    }), 200

@app.put("/api/users/<int:user_id>")
def update_user(user_id):
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET name=?, email=?, password=? WHERE id=?", (name, email, password, user_id))
    conn.commit()
    conn.close()

    return jsonify({
        "success":True,
        "message":"user updated successfully"
    }), 200

#-----------expenses------------------
@app.post("/api/expenses")
def create_expenses():
    data = request.get_json()
    print(data)
    title = data.get("title")
    description = data.get("description")
    amount = data.get("amount")
    date = data.get("date")
    category = data.get("category")
    user_id = data.get("user_id")

    if not data:
        return jsonify({
            "success":False,
            "message":"no data  found to create expense"
        }), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (title, description, amount, date, category, user_id) VALUES (?, ?, ?, ?, ?, ?)", (title, description, amount, date, category, user_id))
    conn.commit()
    conn.close()
    return jsonify({
        "success":True,
        "message":"expense logged successfully"
    }), 201

@app.get("/api/expenses")
def get_expenses():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, category, user_id FROM expenses")
    rows = cursor.fetchall()
    print(rows)
    conn.close()

    expenses = []
    for row in rows:
        expense = {"id":row["id"], "title":row["title"], "category":row["category"], "user_id":row["user_id"]}
        expenses.append(expense)
    return jsonify({
        "success":True,
        "message":"expenses retrieved",
        "data":expenses
    }), 200

@app.get("/api/expenses/<int:expense_id>")
def get_expense(expense_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses WHERE id=?", (expense_id,))
    row = cursor.fetchone()
    conn.close()
    print(row)
    

    if not row:
        return jsonify({
            "success":False,
            "message":"expense not found"
        }), 404
    
    return jsonify({
        "success":True,
        "message":"expense retrieved",
        "data":dict(row)
    }), 200

@app.delete("/api/expenses/<int:expense_id>")
def delete_expense_by_id(expense_id):
    conn = sqlite3.connect(DB_NAME)
    cursor =  conn.cursor()
    cursor.execute("SELECT * FROM expenses WHERE id=?", (expense_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({
            "success":False,
            "message":"expense not found"
        }), 404
    cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()
    conn.close()

    return jsonify({
        "success":True,
        "message":"user deleted successfully"
    }), 200


@app.put("/api/expenses/<int:expense_id>")
def update_expense_by_id(expense_id):
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    amount = data.get("amount")
    date_str = data.get("date")
    category = data.get("category")
    user_id = data.get("user_id")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE expenses
            SET title=?, description=?, amount=?, date=?, category=?, user_id=?
            WHERE id=?
        """, (title, description, amount, date_str, category, user_id, expense_id))
        conn.commit()

        return jsonify({
            "success":True,
            "message":"expense updated sucessfully"
        }), 200
    except sqlite3.IntegrityError as e:
        #integrityerror is most likely when an attribute has any specific options

        return jsonify({
            "error":f"something went wrong: {str(e)}"
        }), 400
    except sqlite3.OperationalError as e:
        #OperationalError wraps sql syntax errors, missing table/column
        return jsonify({"error":f"database operational error: {str(e)}"}), 500
    except sqlite3.DatabaseError as e:
        #DatabaseError is for general database errors
        return jsonify({"error":f"Database error {str(e)}"})
    finally:
        conn.close()


#---------------- Frontend (HTML + Jinja)--------------
#Frontend
@app.get("/")
def home():
    return render_template("home.html")

@app.get("/about")
def about():
    name = "Reece Rollins"
    hobbies = ['skateboarding','hunting']
    return render_template("about.html", name=name, hobbies=hobbies)

@app.get("/contact_me")
def contact_me():
    contact_info = {
        "email": "rrpieces@gmail.com",
        "phone": "208-310-3110",
        "address": "302 elk creek rd idahocity, id 83231"

    }
    return render_template("contact_me.html", contact_info=contact_info)



if __name__ == "__main__":
    init_db()
    app.run(debug=True)