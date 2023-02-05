from libgen_api import LibgenSearch
from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

#connect to db
def get_db():
    DATABASE = 'books.db'
    con = sqlite3.connect(DATABASE)
    con.row_factory = sqlite3.Row
    return con

def fixTitle(bookDict):
    for x in bookDict:
        for y in x:
            if y == 'Title':
                title = x.get(y)
                if 'ISBN' in title:
                    newTitle = title.split("ISBN")[0]
                    x.update({y: newTitle})
                elif 'ASIN' in title:
                    newTitle = title.split("ASIN")[0]
                    x.update({y: newTitle})
    return bookDict


def searchForBook(bookTitle, authorName):
    s = LibgenSearch()
    title_filters = {"Language": "English"}
    results = s.search_book_filtered_fiction(
        bookTitle, authorName, title_filters, exact_match=False)
    finalResults = fixTitle(results)
    return finalResults


@app.route('/addBook', methods=['POST', 'GET'])
def addBookModal():
    con = get_db() 
    cur = con.cursor() 

    if request.method == 'POST':
        try:
            title = request.form["title"]
            author = request.form["author"]
            link = request.form["link"]
            pages = request.form["pages"]
            year = request.form["year"]
            args = (title, author, pages, year, link)

            cur.execute("INSERT INTO BOOKS (title, author, pages, year, link) VALUES (?, ?, ?, ?, ?)", args)
            con.commit()
            print('Book successfully added!')
        except:
            con.rollback()
            print('Book could not be added :(')
        finally:
            return redirect("booklist")
    elif request.method == 'GET':
        return redirect("booklist")


@app.route('/editBook', methods=['POST'])
def editBookModal():
    con = get_db() 
    cur = con.cursor()

    if request.method == 'POST':
        try:
            title = request.form["title"]
            author = request.form["author"]
            link = request.form["link"]
            pages = request.form["pages"]
            year = request.form["year"]
            DBid = request.form["id"]

            args = (title, author, pages, year, link, DBid)

            cur.execute("UPDATE BOOKS SET title = ?, author = ?, pages = ?, year = ?, link = ? WHERE ROWID = ?", args)
            con.commit()
            print('Book successfully updated!')
        except:
            con.rollback()
            print('Book could not be updated :(')
        finally:
            return redirect("booklist")

@app.route('/deleteBook/<DBid>')
def deleteBook(DBid):
    con = get_db()
    cur = con.cursor()

    try:
        args = (DBid, )

        cur.execute("DELETE FROM BOOKS WHERE ROWID = ?", args)
        con.commit()
        print('Book successfully deleted!')
        cur.execute("SELECT * FROM BOOKS")
        con.commit();
    except:
        con.rollback()
        print('Book could not be deleted :(')
    finally:
        rows = cur.fetchall()  
        return render_template("booklist.html", rows = rows)

@app.route('/', methods=['POST'])
def search():
    bookTitle = request.form['bookTitle']
    authorName = request.form['authorName']
    bookResult = searchForBook(bookTitle, authorName)
    # processed_text = text.upper()
    return render_template("index.html", bookList=bookResult)


@ app.route("/")
def home():
    return render_template("index.html")


@ app.route("/booklist")
def booklist():
    con = get_db()
    cur = con.cursor()  

    try:
        cur.execute("SELECT * FROM BOOKS")
        con.commit();
    except:
        print('Could not get all books :(')
    finally:
        rows = cur.fetchall()  
        return render_template("booklist.html", rows = rows)


@ app.route('/redirect_to')
def redirect_to():
    link = request.args.get('link')
    return redirect(link), 301


if __name__ == "__main__":
    app.run(debug=True)
