from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# Replace 'your_ip_address' with the actual IP of your MariaDB server
DB_HOST = "127.0.0.1"  # Change to your MySQL server IP if hosted on another machine
DB_USER = "your_user"  # Replace with your MySQL username
DB_PASSWORD = "your_password"  # Replace with your MySQL password
DB_NAME = "mydb"  # Replace with your database name

# Connect to the database
def get_db_connection():
    try:
        db = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return db
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

@app.route('/receive', methods=['POST'])
def receive_data():
    data = request.json  # Expecting JSON data

    if not data or "username" not in data or "message" not in data:
        return jsonify({"error": "Invalid request"}), 400

    username = data["username"]
    message = data["message"]

    db = get_db_connection()
    if db is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = db.cursor()

    # Create a new table for the user if it does not exist
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS `{username}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        message TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(create_table_query)

    # Insert data into the user's table
    insert_query = f"INSERT INTO `{username}` (message) VALUES (%s);"
    cursor.execute(insert_query, (message,))
    
    db.commit()
    cursor.close()
    db.close()

    return jsonify({"success": True, "message": "Data stored successfully"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)  # Expose Flask server on all interfaces
