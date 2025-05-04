from flask import Flask, request, render_template_string, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
import pymysql
from datetime import datetime
import os
from dotenv import load_dotenv
import secrets
import jwt
from jwt.exceptions import InvalidTokenError

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management

# Initialize OAuth
oauth = OAuth(app)

# Configure Google OAuth
google = oauth.register(
    name='google',
    client_id='764547220294-f0eesku49smdiioa9riv3ufvojd462ak.apps.googleusercontent.com',
    client_secret='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',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid profile email',
        'token_endpoint_auth_method': 'client_secret_post',
        'token_placement': 'header'
    }
)

# JWT Public Key
PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAEMU1JFVEO9FkVr0r041GpAWzKvQi1TBYm
arJj3+aNeC2aK9GT7Hct1OJGWQGbUkNWTeUr+Ui09PjBit+AMYuHgA==
-----END PUBLIC KEY-----
"""

# Test Public Key
#PUBLIC_KEY = """
#-----BEGIN PUBLIC KEY-----
#MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEPZMFXyt1AXtUOBLMPhOEsZLfZVv9
#tl3kKvFvyyimYsXmPz+oDPuMm4INw53k/tjonx7/p1Ufytiniz9F2j4dZw==
#-----END PUBLIC KEY-----
#"""

db_config = {
    'host': '34.102.20.203',
    'user': 'pom-webapp',
    'password': '"ceOA"QhG>fJ%5vA',
    'database': 'pom-records',
    'autocommit': True
}

def is_jwt_token(text):
    parts = text.strip().split('.')
    return len(parts) == 3

def verify_jwt_token(token):
    try:
        jwt.decode(token, PUBLIC_KEY, algorithms=["ES256"])
        return True
    except InvalidTokenError:
        return False

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Vulnerable Input Demo</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap');
        
        body {
            font-family: 'Patrick Hand', cursive;
            background-color: white;
            color: #333;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }

        h1, h2 {
            text-align: center;
            font-weight: 400;
            margin-bottom: 30px;
            color: #ea826f;
        }

        .disabled {
            opacity: 0.5;
            pointer-events: none;
        }

        .login-button {
            background-color: #ea826f;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            font-family: 'Patrick Hand', cursive;
            font-size: 1.2em;
            transition: transform 0.2s;
        }

        .login-button:hover {
            transform: scale(1.05);
        }

        .submit-button {
            background-color: #ea826f;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-family: 'Patrick Hand', cursive;
            font-size: 1.2em;
            transition: transform 0.2s;
        }

        .submit-button:hover {
            transform: scale(1.05);
        }

        .logout-button {
            background-color: #ea826f;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-family: 'Patrick Hand', cursive;
            font-size: 1.2em;
            transition: transform 0.2s;
        }

        .logout-button:hover {
            transform: scale(1.05);
        }

        .user-info {
            margin: 20px 0;
            text-align: center;
            font-size: 1.2em;
        }

        .valid-jwt {
            background-color: rgba(223, 57, 28, 0.74);
        }

        form {
            text-align: center;
            margin-bottom: 30px;
        }

        input[type="text"] {
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 8px;
            margin-right: 10px;
            width: 300px;
            font-family: 'Patrick Hand', cursive;
            font-size: 1.1em;
            color: #333;
        }

        table {
            width: 80%;
            margin: 0 auto;
            border-collapse: collapse;
            background-color: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        th, td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }

        th {
            background-color: #f8f8f8;
            font-weight: 400;
        }
    </style>
</head>
<body>
    <h1>Submit Text</h1>
    {% if 'user' in session %}
        <div class="user-info">
            Logged in as: {{ session['user']['email'] }}
            <a href="{{ url_for('logout') }}" class="logout-button">Logout</a>
        </div>
    {% endif %}
    
    <form method="POST" action="{{ url_for('submit') }}">
        <input type="text" name="user_input" placeholder="Enter text" {% if 'user' not in session %}class="disabled"{% endif %}>
        {% if 'user' in session %}
            <button type="submit" class="submit-button">Submit</button>
        {% else %}
            <a href="{{ url_for('login') }}" class="login-button">Login with Google</a>
        {% endif %}
    </form>

    <h2>Submissions</h2>
    <table border="1">
        <tr><th>Text</th><th>Timestamp</th></tr>
        {% for row in rows %}
            <tr {% if row[2] %}class="valid-jwt"{% endif %}>
                <td>{{ row[0] }}</td>
                <td>{{ row[1] }}</td>
            </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.route("/")
def index():
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    
    # Load current submissions
    cursor.execute("SELECT text_input, submitted_at, is_valid_jwt FROM submissions ORDER BY submitted_at DESC")
    rows = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template_string(HTML_TEMPLATE, rows=rows)

@app.route('/login')
def login():
    # Generate a random nonce
    nonce = secrets.token_urlsafe(16)
    session['oauth_nonce'] = nonce
    
    # Include nonce in the authorization request
    return google.authorize_redirect(
        redirect_uri=url_for('authorized', _external=True),
        nonce=nonce
    )

@app.route('/login/authorized')
def authorized():
    # Get the nonce from the session
    nonce = session.pop('oauth_nonce', None)
    
    # Get the token and user info
    token = google.authorize_access_token()
    user_info = google.parse_id_token(token, nonce=nonce)
    
    # Store user info in session
    session['user'] = user_info
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route("/submit", methods=["POST"])
def submit():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    
    user_input = request.form["user_input"]
    is_valid_jwt = False
    
    # Check if the input is a JWT token and verify it
    if is_jwt_token(user_input):
        is_valid_jwt = verify_jwt_token(user_input)
    
    # 🔥 Deliberately vulnerable to SQL Injection
    query = f"INSERT INTO submissions (text_input, submitted_at, is_valid_jwt) VALUES ('{user_input}', '{datetime.now()}', {is_valid_jwt});"
    print("Executing SQL:", query)
    
    try:
        cursor.execute(query)
    except Exception as e:
        print("SQL Error:", e)
    
    cursor.close()
    conn.close()
    
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)