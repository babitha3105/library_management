from flask import Flask, request, render_template, session, redirect,flash
import sqlite3

app = Flask(__name__)

app.secret_key = "mysecretkey"


@app.route("/")
def home():
    return render_template("login.html")


@app.route("/login", methods=['POST'])
def login():

    username = request.form['user']
    password = request.form['pass']

    if username == 'admin' and password == '1234':

        session['user'] = username

        return redirect("/books")

    else:
       flash("Invalid username or password", "danger")
       return redirect("/")

@app.route('/addbook')
def addbookpage():
    if 'user' not in session:
        return redirect('/')

    return render_template('addbook.html')
    
@app.route("/add", methods=['POST'])
def add_book():
    title=request.form["title"]
    author=request.form["author"]
    category=request.form["category"]
    quantity=request.form["quantity"]

    conn=sqlite3.connect("library.db")
    cur=conn.cursor()
    cur.execute("INSERT INTO books(title,author,category,quantity) VALUES(?,?,?,?)",(title,author,category,quantity))
    conn.commit()
    conn.close()
    flash("Book added successfully!", "success")
    return redirect('/books')


@app.route("/books")
def viewbook():
    if 'user' not in session:
        return redirect('/')
    search=request.args.get("search")
    conn = sqlite3.connect("library.db")
    cur = conn.cursor()
    if search:
        cur.execute("""SELECT * FROM books where title LIKE ? """, ('%' + search + '%',))
    else:
        cur.execute("SELECT * FROM books")

    books = cur.fetchall()

    conn.close()

    return render_template("books.html", books=books)


@app.route('/delete/<int:id>')
def delete(id):
    conn=sqlite3.connect('library.db')
    cur=conn.cursor()
    cur.execute("DELETE FROM books WHERE id= ? ",(id,))
    conn.commit()
    conn.close()
    flash("Book deleted successfully!", "danger")
    return redirect('/books')
@app.route('/edit/<int:id>')

def edit(id):
    conn=sqlite3.connect('library.db')
    cur=conn.cursor()
    cur.execute("SELECT * FROM books WHERE id = ? ",(id,))
    book=cur.fetchone()
    conn.close()
    return render_template("edit.html", book=book)

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    title=request.form["title"]
    author=request.form["author"]
    category=request.form["category"]
    quantity=request.form["quantity"]

    conn=sqlite3.connect('library.db')
    cur=conn.cursor()
    cur.execute("UPDATE books SET title = ?, author = ?, category = ? ,quantity=? WHERE id = ?", (title,author,category,quantity,id))
    conn.commit()
    conn.close()
    return redirect('/books')

@app.route('/issue')
def issue_page():

    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect("library.db")
    cur = conn.cursor()

    cur.execute("""SELECT * FROM books WHERE quantity > 0""")
    books = cur.fetchall()

    conn.close()

    return render_template("issue.html", books=books)



from datetime import datetime, timedelta

@app.route('/issuebook', methods=['POST'])
def issue_book():

    student = request.form['student']
    book_id = request.form['book_id']
    issue_date = request.form['issue_date']

    # convert string to date
    issue = datetime.strptime(issue_date, "%Y-%m-%d")

    # add 7 days
    return_date = issue + timedelta(days=7)

    # convert back to string
    return_date = return_date.strftime("%Y-%m-%d")

    conn = sqlite3.connect("library.db")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO issued(student_name, book_id, issue_date, return_date)
        VALUES (?, ?, ?, ?)
    """, (student, book_id, issue_date, return_date))

    # reduce quantity
    cur.execute("""
        UPDATE books
        SET quantity = quantity - 1
        WHERE id = ?
    """, (book_id,))

    conn.commit()
    conn.close()

    return redirect('/books')

@app.route('/issuedbooks')
def viewissued():
    if 'user' not in session:
        return redirect('/')
    conn=sqlite3.connect('library.db')
    cur=conn.cursor()
    cur.execute('''SELECT issued.student_name,books.title,issued.issue_date,issued.return_date,issued.id FROM issued JOIN books ON issued.book_id = books.id''')
    issued=cur.fetchall()
    conn.close()
    return render_template('issued_books.html',issued=issued)


@app.route('/return/<int:id>')
def return_book(id):

    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect("library.db")
    cur = conn.cursor()

    # get book_id first
    cur.execute("""
        SELECT book_id
        FROM issued
        WHERE id = ?
    """, (id,))

    book = cur.fetchone()

    book_id = book[0]

    # increase quantity
    cur.execute("""
        UPDATE books
        SET quantity = quantity + 1
        WHERE id = ?
    """, (book_id,))

    # remove issued record
    cur.execute("""
        DELETE FROM issued
        WHERE id = ?
    """, (id,))

    conn.commit()
    conn.close()

    return redirect('/issuedbooks')
@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect("library.db")
    cur = conn.cursor()

    # total books
    cur.execute("SELECT COUNT(*) FROM books")
    total_books = cur.fetchone()[0]

    # available books
    cur.execute("SELECT SUM(quantity) FROM books")
    available_books = cur.fetchone()[0]

    # issued books
    cur.execute("SELECT COUNT(*) FROM issued")
    issued_books = cur.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        total_books=total_books,
        available_books=available_books,
        issued_books=issued_books
    )

@app.route('/logout')
def logout():

    session.pop('user', None)                                                                    #logout
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)