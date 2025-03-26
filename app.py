from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import random


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///passwords.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#Password Model
class Password(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(100), nullable=False)

#Brukte hjelp av ChatGPT her
with app.app_context():
    db.create_all()

password_length: int = 8
randomcharsupper: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
randomcharslower: str = "abcdefghijklmnopqrstuvwxyz"
randomnumbers: str = "0123456789"
randomsymbols: str = "!@#$%^&*()"
saved_passwords: list = []

newpasword: str  = ""
password: str = ""
error_message: str = ""


def generate_random_password():
    '''
    Generates a password from a list using a for-loop
    '''
    global newpasword
    global password
    global password_length
    global error_message

    attempts = 0
    error_message = ""
    randomcharlist = ""

    length_input = request.form.get('length')
    if length_input:
        password_length = int(length_input)


    if request.form.get('lowercase'):
        randomcharlist += randomcharslower
    
    if request.form.get('uppercase'):
        randomcharlist += randomcharsupper

    if request.form.get('symbols'):
        randomcharlist += randomsymbols

    if request.form.get('numbers'):
        randomcharlist += randomnumbers
    
    if randomcharlist != "" and password_length != '':
        while True:
            for i in range(0, password_length):
                password = password + random.choice(randomcharlist)
            newpasword = password
            password = ""
            eligiblepass = check_userpass(newpasword)
            if eligiblepass or attempts >= 1000:
                if attempts >= 1000:
                    error_message = "Password might not have generated correctly"
                break
            else:
                attempts += 1
                continue
    else: 
        newpasword = "" 
        error_message = "invalid preferences"

def check_userpass(userpass: str) -> bool:
    '''
    Checks if the password fits all the selected preferences
    '''
    if request.form.get('lowercase'):
        has_lower = userpass.upper() != userpass 
    else:
        has_lower = True
    if request.form.get('uppercase'):
        has_upper = userpass.lower() != userpass
    else:
        has_upper = True
    if request.form.get('numbers'):
        has_number = any(ch.isdigit() for ch in userpass)
    else:
        has_number = True
    if request.form.get('symbols'):
        has_symbol = any(ch in randomsymbols for ch in userpass)
    else:
        has_symbol = True

    return has_lower and has_upper and has_number and has_symbol

@app.route("/", methods=["POST", "GET"])
def home():
    global newpasword
    if request.method == 'POST':
        if request.form.get('generate_button') == 'Generate':
            generate_random_password()
        elif request.form.get('save_button') == 'Save':
            saved_password = request.form.get("password_value")
            if saved_password:
                new_entry = Password(value=saved_password)
                db.session.add(new_entry)
                db.session.commit()
        elif request.form.get('clear_button') == 'Clear Saved Passwords':
            with app.app_context():
                db.session.query(Password).delete()
                db.session.commit()
        return redirect("/") 
    
    saved_passwords = Password.query.all()
    return render_template('index.html', randpass=newpasword, errormessage=error_message, passwords=saved_passwords)

if __name__ == "__main__":
    app.run()
