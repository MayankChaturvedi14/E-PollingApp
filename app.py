import os
import re
from sqlite3.dbapi2 import Connection, Cursor, IntegrityError, connect, Error
from flask import Flask,render_template, request, redirect,session
import sqlite3 as sql
from flask_ngrok import run_with_ngrok


from werkzeug.utils import redirect

filename = 'data.txt'

app= Flask(__name__)
app.secret_key=os.urandom(24)
#run_with_ngrok(app)

poll_data = {
   'question' : 'Which organisation do you support?',
   'fields'   : ["Bharatiya Janata Party", "Indian National Congress", "Communist Party of India (Marxist)",	
                "Communist Party of India", "Bahujan Samaj Party", "Nationalist Congress Party", " All India Trinamool Congress", "Samajwadi Party","National People's Party"]}


@app.route('/')
def index():
    return render_template('P_I_home.html')

@app.route('/ehome')
def ehome():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('loginPage.html')    

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/admin_site')
def admin_site():
    return render_template('admin_site.html')

@app.route('/home')
def home():
    if 'VoterNumber' in session:
        return redirect('/pollbaazi')
    else:
        return redirect('/ehome')

@app.route('/register')
def register():
    return render_template('registrationform.html')

@app.route('/add_voter', methods=['POST'])
def add_voter():
    if request.method == 'POST':
        try:
            name=request.form.get('name')
            Address= request.form.get('Address')
            phone= request.form.get('phone')
            An= request.form.get('An')
            Vn= request.form.get('Vn')
            DOB= request.form.get('DOB')
            Gender= request.form.get('Gender')
            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("""INSERT INTO `registrationform`  (`Name`, `Address`, `MobileNumber`, `AadharNumber`, `VoterNumber`, `DOB`,`Gender`) VALUES('{}', '{}', '{}', '{}', '{}', '{}','{}')""".format(name, Address, phone, An, Vn, DOB,Gender))
                con.commit()
                msg="Hey! {} Your Registration is Sucessfull".format(name)
                return render_template('message.html', msg=msg)
                

        except:
            if "IntegrityError":

                con.rollback()
                con.close()
                return render_template("user_error.html")

            else:
                return("Please Enter Your Data Correctly")

            

@app.route('/login_validation', methods=['POST'])
def login_validation():
    if request.method == 'POST':
        Vn = request.form.get('Vn')
        DOB = request.form.get('DOB')
            
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("""SELECT * FROM `registrationform` WHERE `VoterNumber` LIKE '{}' AND DOB LIKE '{}'""".format(Vn, DOB))
            users = cur.fetchall()
            if len(users)>0:
                try:
                    session['VoterNumber']=users[0][4]
                    VoterNumber=users[0][4]
                    cur.execute("""INSERT INTO `Voted_Users` (`VoterNumber`) VALUES ('{}')""".format(VoterNumber))
                    con.commit()
                    return redirect('/home')

                except IntegrityError:
                    return render_template('voted.html')

            else:
                return render_template('login_error.html')

@app.route('/logout')
def logout():
    session.pop('VoterNumber')
    return redirect('/home')

@app.route('/pollbaazi')
def pollbaazi():
    if 'VoterNumber' in session:
         session.pop('VoterNumber')
         return render_template('voting.html', data=poll_data)

    else:
        return redirect('/ehome')


@app.route('/votingoperation')
def poll():
    vote = request.args.get('field')
 
    out = open(filename, 'a')
    out.write( vote + '\n' )
    out.close()
    
    return render_template('thankyou.html', data=poll_data)

@app.route('/admin_results')
def show_results():
    votes = {}
    for f in poll_data['fields']:
        votes[f] = 0
 
    f  = open(filename, 'r')
    for line in f:
        vote = line.rstrip("\n")
        votes[vote] += 1
 
    if 'username' in session:
        return render_template('results.html', data=poll_data, votes=votes)
    else:
        return redirect('/ehome')


@app.route('/admin_login', methods=['POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('UserName')
        password = request.form.get('Password')
        with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("""SELECT * FROM `admin_login` WHERE `Username` LIKE '{}' AND `Password` LIKE '{}'""".format(username, password))
                admin = cur.fetchall()
        if len(admin)>0:
            session['username']=admin[0][0]
            return render_template('admin_site.html')

        else:
            return  render_template('admin_message.html')

    else:
        return """<h3> 
                        <b>Please Enter Values Correctly</b>
                        
                        </h3>"""

     
     
@app.route('/show_list')
def show_list():
    con = sql.connect("database.db")
    cur= con.cursor()
    cur.execute("""SELECT * FROM `Voted_Users`""")
    list = cur.fetchall()
    list = [re.sub(r'([0-9\.])\(.*?\n', r'\1', x[0]) for x in list]

    if 'username' in session:

        return render_template('list.html', list=list)

    else:
        return redirect('/ehome')

@app.route('/admin_logout')
def admin_logout():
    session.pop('username')
    return redirect('/ehome')

@app.route('/about')
def about():
    return render_template('devs.html')

@app.route('/help')
def help():
    return render_template('help.html')
if __name__ == '__main__':
    app.run(debug=True)
