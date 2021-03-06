# Store this code in 'app.py' file
  
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import pymysql.cursors
import os
import re
  
  
app = Flask(__name__)
  
  
app.secret_key = 'your secret key'
  
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_flask'
  
mysql = MySQL(app)
  
#@app.route('/')
@app.route('/', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return render_template('index.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)
  
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
  
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO user VALUES (NULL, % s, % s, % s)', (username, password, email, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)

conn = cursor = None
#fungsi koneksi database


def openDb():
   global conn, cursor
   conn = pymysql.connect(host='localhost', port=3306,
                          user='root', passwd='', db='db_flask')
   cursor = conn.cursor()
#fungsi untuk menutup koneksi


def closeDb():
   global conn, cursor
   cursor.close()
   conn.close()
#fungsi view index() untuk menampilkan data dari database


@app.route('/dashboard')
def index():
   openDb()
   container = []
   sql = "SELECT * FROM barang"
   cursor.execute(sql)
   results = cursor.fetchall()
   for data in results:
      container.append(data)
   closeDb()
   return render_template('index.html', container=container,)

#fungsi view tambah() untuk membuat form tambah


@app.route('/tambah', methods=['GET', 'POST'])
def tambah():
   if request.method == 'POST':
      nama = request.form['nama']
      harga = request.form['harga']
      stok = request.form['stok']
      openDb()
      sql = "INSERT INTO barang (nama_barang, harga,stok) VALUES (%s, %s, %s)"
      val = (nama, harga, stok)
      cursor.execute(sql, val)
      conn.commit()
      closeDb()
      return redirect(url_for('index'))
   else:
      return render_template('tambah.html')
#fungsi view edit() untuk form edit


@app.route('/edit/<id_barang>', methods=['GET', 'POST'])
def edit(id_barang):
   openDb()
   cursor.execute('SELECT * FROM barang WHERE id_barang=%s', (id_barang))
   data = cursor.fetchone()
   if request.method == 'POST':
      id_barang = request.form['id_barang']
      nama = request.form['nama']
      harga = request.form['harga']
      stok = request.form['stok']
      sql = "UPDATE barang SET nama_barang=%s, harga=%s, stok=%s WHERE id_barang=%s"
      val = (nama, harga, stok, id_barang)
      cursor.execute(sql, val)
      conn.commit()
      closeDb()
      return redirect(url_for('index'))
   else:
      closeDb()
      return render_template('edit.html', data=data)
#fungsi untuk menghapus data


@app.route('/hapus/<id_barang>', methods=['GET', 'POST'])
def hapus(id_barang):
   openDb()
   cursor.execute('DELETE FROM barang WHERE id_barang=%s', (id_barang,))
   conn.commit()
   closeDb()
   return redirect(url_for('index'))


if __name__ == '__main__':
   app.run(debug=True)
