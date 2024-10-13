from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from shopping_list_sorter import ShoppingListSorter
from test_shopping_list import test_shopping_list
import re
import mysql.connector
from mysql.connector import errorcode

app = Flask(__name__)
CORS(app)

sorter = ShoppingListSorter()

# Funkce pro připojení k databázi
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host='pybali.mysql.pythonanywhere-services.com',
            user='pybali',
            password='balihodb',  # Zde vlož své heslo
            database='pybali$default'  # Zde použij správný název databáze
        )
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Nesprávné uživatelské jméno nebo heslo")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Databáze neexistuje")
        else:
            print(err)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.get_json()
        if data and 'shopping_list' in data:
            input_list = data['shopping_list']
            shopping_list = [item.strip() for item in re.split(r'[,\n]+', input_list) if item.strip()]
            sorted_list = sorter.sort_shopping_list(shopping_list)
            return jsonify(sorted_list)
        else:
            return jsonify({'error': 'Invalid input'}), 400
    return render_template('index.html', test_list=test_shopping_list)

@app.route('/test_list', methods=['GET'])
def get_test_list():
    return jsonify(test_shopping_list.split(','))

@app.route('/submit_report', methods=['POST'])
def submit_report():
    data = request.get_json()
    if data and 'input_list' in data and 'sorted_list' in data and 'report' in data:
        input_list = data['input_list']
        sorted_list = data['sorted_list']
        report = data['report']

        # Uložení reportu do databáze
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO reports (input_list, sorted_list, report) VALUES (%s, %s, %s)', (input_list, sorted_list, report))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'message': 'Report was successfully submitted!'}), 200
        else:
            return jsonify({'error': 'Database connection failed'}), 500
    else:
        return jsonify({'error': 'Invalid report data'}), 400

@app.route('/reports', methods=['GET'])
def get_reports():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM reports')
        reports = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(reports), 200
    else:
        return jsonify({'error': 'Database connection failed'}), 500


if __name__ == '__main__':
    app.run(debug=True)
