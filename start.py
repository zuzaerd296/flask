# Dołączanie modułu flask 

from flask import Flask
from flask import render_template, request, redirect, url_for, flash, session
from flask import Flask, session
from flask_session import Session
import sqlite3

# Tworzenie aplikacji
app = Flask("Flask - Lab")

# Tworzenie obsługi sesji
sess = Session()

# Ścieżka do pliku bazy danych w sqlite
DATABASE = 'database.db'

@app.route('/create_database', methods=['GET', 'POST'])
def create_db():
    # Połączenie sie z bazą danych
    conn = sqlite3.connect(DATABASE)
    # Stworzenie tabeli w bazie danych za pomocą sqlite3
    conn.execute('CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, type TEXT)')
    conn.execute('CREATE TABLE books (title TEXT, author TEXT)')
    # Dodanie użytkowników i książek do tebel
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username, password, type) VALUES (?, ?, ?)", ('zuza', '1234', 'user'))
    cur.execute("INSERT INTO users (username,password,type) VALUES (?,?,?)",('admin','admin','admin') )
    cur.execute("INSERT INTO books (title,author) VALUES (?,?)",('Narnia','C.S. Lewis') )
    cur.execute("INSERT INTO books (title,author) VALUES (?,?)",('Mały książe','Antoine de Saint-Exupéry') )
    conn.commit()
    # Zakończenie połączenia z bazą danych
    conn.close()
    return index()


@app.route('/', methods=['GET', 'POST'])
def index():
    # Sprawdzenie czy w sesji dla danego klienta zapisana jest nazwa użytkownika
    if 'user' in session:
        user_type=session['user']
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        cur.execute("select * from books")
        books = cur.fetchall()
        
        if user_type == "admin":
            return render_template('main.html', books = books) + "<br> <a href=/users>List of users</a> <br>"
        else:
            return render_template('main.html', books = books)
    else:
        return render_template('loging.html')


@app.route('/login', methods=['POST'])
def login():
    login = request.form['login']
    password = request.form['password']

    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (login, password))
    user = cur.fetchone() 
    con.close()

    if user:
        session['user'] = user[3]
        return index()

    return "Błąd logowania. Sprawdź dane logowania i spróbuj ponownie. <br>" + index()


@app.route('/users', methods=['GET', 'POST'])
def list_of_users():
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        cur.execute("select * from users")
        users = cur.fetchall()
        return render_template('users_list.html', users=users)


@app.route('/user_details/<int:user_id>', methods=['GET'])
def user_details_id(user_id):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cur.fetchone()
    con.close()

    if user:
        # Przekazanie danych użytkownika do widoku
        return render_template('user_details.html', user=user)
    else:
        # Obsłuż sytuację, gdy użytkownik o podanym ID nie istnieje
        return "Użytkownik o podanym ID nie istnieje."
    

@app.route('/user_details/<string:user_name>', methods=['GET'])
def user_details_name(user_name):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (user_name,))
    user = cur.fetchone()
    con.close()

    if user:
        # Przekazanie danych użytkownika do widoku
        return render_template('user_details.html', user=user)
    else:
        # Obsłuż sytuację, gdy użytkownik o podanym ID nie istnieje
        return "Użytkownik o podanej nazwie nie istnieje."
    


@app.route('/add-user', methods=['POST'])
def add_user():
        login = request.form['login']
        password = request.form['password']
        type=request.form['type']
        # Dodanie użytkownika do bazy danych
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        cur.execute("INSERT INTO users (username,password,type) VALUES (?,?,?)",(login,password,type) )
        con.commit()
        con.close()
        return "Dodano użytkownika do bazy danych <br>" + index()


@app.route('/add-book', methods=['POST'])
def add_book():
        title = request.form['title']
        author = request.form['author']
        # Dodanie użytkownika do bazy danych
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        cur.execute("INSERT INTO books (title,author) VALUES (?,?)",(title,author) )
        con.commit()
        con.close()
        return "Dodano książkę do bazy danych <br>" + index()


@app.route('/logout', methods=['GET'])
def logout():
    # Jeżeli sesja klienta istnieje - usunięcie sesji 
    if 'user' in session:
        session.pop('user')
    else:
        # Przekierowanie klienta do strony początkowej
        redirect(url_for('index'))
    
    return "Wylogowano <br>" + index()

# Uruchomienie aplikacji w trybie debug
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
sess.init_app(app)
app.config.from_object(__name__)
app.debug = True
app.run()