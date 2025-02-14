from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
from mysql.connector import Error
import mysql.connector
from database import host, user, password, database

app = Flask (__name__)
ma=Marshmallow(app)

class MemberSchema(ma.Schema):
    name = fields.String(required = True)
    age = fields.String(required=True)
    email = fields.String(required=True)
    phone_number = fields.String(required=True)
    
    class Meta:
        fields=("id","name","age","email","phone_number")

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host = host,
            user = user,
            password = password,
            database = database
        )
        print("connection successful")
        return conn
    except mysql.connector.Error as err:
        if err.errno == 2003:
            print("Check hostname/ip,port, and, firewall")
        elif err.errno == 1045: 
            print("Error: Check username and password")
        elif err.errno == 1049:
            print("Error: check if database exists")
        else:
            print(f"Error: {err}")
            return None

@app.route("/")
def home():
    return "welcome to the gym application"

@app.route('/members', methods = ['GET'])
def get_members():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error":"Database connection failed"}), 50
        cursor = conn.cursor(dictionary = True)
        query = "SELECT * FROM members"
        cursor.execute(query)
        members = cursor.fetchall()
        return members_schema.jsonify(members)
    
    except Error as e:
        print (f"error : {e}")
        return jsonify({"error": "Internal server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/members', methods = ['POST'])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        print(f"validation error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error":"Connection to database failed"}), 500
        cursor = conn.cursor(dictionary=True)
    
        new_member = (member_data['name'], member_data['age'], member_data['email'], member_data['phone_number'])
        query = "INSERT INTO members (name, age, email, phone_number) VALUES (%s,%s,%s,%s)"
    
        cursor.execute(query, new_member)
        conn.commit()
        return jsonify({"success":"Member added successfully!"}), 201
    except Error as e:
        print (f"Error: {e}")
        return jsonify({"Error":"Internal server error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            


@app.route('/members/<int:id>', methods = ['PUT'])
def update_member(id):
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        print(f"validation error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error":"Connection to database failed"}), 500
        cursor = conn.cursor(dictionary=True)
    
        updated_member = (member_data['name'],member_data["age"], member_data["email"], member_data["phone_number"], id)
        query = 'UPDATE members SET name = %s, age = %s, email = %s, phone_number = %s WHERE id = %s'
        cursor.execute(query, updated_member)
        conn.commit()
        return jsonify({"success":"Member updated successfully!"}), 201
    
    except Error as e:
        print (f"Error: {e}")
        return jsonify({"Error":"Internal server error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            

@app.route('/members/<int:id>', methods = ['DELETE'])
def delete_member(id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error":"Connection to database failed"}), 500
        cursor = conn.cursor(dictionary=True)
        
        member_to_remove =(id,)
        
        cursor.execute("SELECT * FROM members WHERE id = %s", member_to_remove)
        member=cursor.fetchone()
        if not member:
            return jsonify({"Error": "Member not found"}), 404
        query = "DELETE FROM members WHERE id = %s"
        cursor.execute(query,member_to_remove)
        conn.commit()
        
        return jsonify({"success":"Member removed successfully!"}), 201
    
    except Error as e:
        print (f"Error: {e}")
        return jsonify({"Error":"Internal server error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


if __name__ == "__main__":
    app.run(debug=True)