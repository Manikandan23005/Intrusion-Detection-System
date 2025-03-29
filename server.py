from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# Database connection
db = mysql.connector.connect(
    host="your_ip_address",
    user="your_db_user",
    password="your_db_password",
    database="mydb"
)

cursor = db.cursor()

@app.route('/receive_data', methods=['POST'])
def receive_data():
    data = request.json  # Expecting JSON input
    username = data.get("username")  # Unique user identifier
    temperature = data.get("temperature")  # Example data

    if not username or not temperature:
        return jsonify({"error": "Missing data"}), 400

    # Table name based on username (sanitize input to prevent SQL injection)
    table_name = f"user_{username.replace('-', '_')}"  # Replace invalid chars

    # Create table dynamically if not exists
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        temperature FLOAT,
        received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(create_table_query)
    db.commit()

    # Insert data into the user-specific table
    insert_query = f"INSERT INTO {table_name} (temperature) VALUES (%s);"
    cursor.execute(insert_query, (temperature,))
    db.commit()

    return jsonify({"message": f"Data stored in table {table_name}"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Listen on all interfaces
