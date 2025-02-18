from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Configure MySQL connection
db_config = {
    'user': 'root',
    'password': 'Siddhi@123',
    'host': 'localhost',
    'database': 'quiz_app'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        db = get_db_connection()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                           (name, email, hashed_password))
            db.commit()
            flash('You have successfully signed up!', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
            db.rollback()
        finally:
            cursor.close()
            db.close()

    return render_template('signup.html')

# signin
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['name']
                flash('Login successful!', 'success')
                return redirect(url_for('login'))
            else:
                flash('Invalid email or password. Please try again.', 'danger')
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        finally:
            cursor.close()
            db.close()

    return render_template('user_login.html')

# questions for Quiz
questions = [
    {
        "question": "1) Who developed the Python language?",
        "choices": ["Zim Den","Guido van Rossum","Niene Stom","Wick van Rossum"],
        "answer": "Guido van Rossum"
    },
    {
        "question": "2) In which year was the Python language developed?",
        "choices": ["1995", "1972", "1981", "1989"],
        "answer": "1989"
    },
    {
        "question": "3) In which language is Python written?",
        "choices": ["English", "PHP", "C", "all"],
        "answer": "C"
    },
     {
        "question": "4) What do we use to define a block of code in Python language?",
        "choices": ["Key", "Brackets", "Indentation", "none of this"],
        "answer": "Indentation"
    },
     {
        "question": "5) Which of the following is not a keyword in Python language?",
        "choices": ["val", "raise", "try", "with"],
        "answer": "val"
    }
]

@app.route('/')
def index():
    user = session.get('username')
    return render_template('index.html', user=user)

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        score = 0
        for i, question in enumerate(questions):
            user_answer = request.form.get(f'question-{i}')
            if user_answer == question['answer']:
                score += 1
        return redirect(url_for('result', score=score))

    return render_template('quiz.html', questions=questions)


@app.route('/result')
def result():
    score = request.args.get('score', 0, type=int)
    return render_template('result.html', score=score, total=len(questions))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)


