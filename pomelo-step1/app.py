from flask import Flask, request, render_template_string
import pymysql
from datetime import datetime

app = Flask(__name__)

db_config = {
    'host': '34.102.20.203',
    'user': 'pom-webapp',
    'password': '"ceOA"QhG>fJ%5vA',
    'database': 'pom-records',
    'autocommit': True
}

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
    <form method="POST">
        <input type="text" name="user_input" placeholder="Enter text">
        <button type="submit" class="submit-button">Submit</button>
    </form>
    <h2>Submissions</h2>
    <table border="1">
        <tr><th>Text</th><th>Timestamp</th></tr>
        {% for row in rows %}
            <tr><td>{{ row[0] }}</td><td>{{ row[1] }}</td></tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()

    if request.method == "POST":
        user_input = request.form["user_input"]

        # 🔥 Deliberately vulnerable to SQL Injection
        query = f"INSERT INTO submissions (text_input, submitted_at) VALUES ('{user_input}', '{datetime.now()}');"
        print("Executing SQL:", query)

        try:
            cursor.execute(query)
        except Exception as e:
            print("SQL Error:", e)

    # Load current submissions
    cursor.execute("SELECT text_input, submitted_at FROM submissions ORDER BY submitted_at DESC")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template_string(HTML_TEMPLATE, rows=rows)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)