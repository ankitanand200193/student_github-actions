from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
from bson.regex import Regex
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)  # Replace with your MongoDB URI
db = client["student_db"]  # Database name
students_collection = db["students"]  # Collection name

# Database functions
def add_student(data):
    student = {"name": data["name"], "age": data["age"]}
    result = students_collection.insert_one(student)
    student["_id"] = str(result.inserted_id)  # Convert ObjectId to string
    return student

def get_students():
    return [{"_id": str(student["_id"]), "name": student["name"], "age": student["age"]} for student in students_collection.find()]

def get_student_by_id(student_id):
    student = students_collection.find_one({"_id": ObjectId(student_id)})
    if student:
        student["_id"] = str(student["_id"])  # Convert ObjectId to string
    return student

def delete_student(student_id):
    result = students_collection.delete_one({"_id": ObjectId(student_id)})
    if result.deleted_count > 0:
        return {"message": "Deleted"}
    return {"error": "Student not found"}

# Flask routes
@app.route('/')
def home():
    return "Welcome to the Student Management System API!", 200

@app.route('/students', methods=['POST'])
def add():
    data = request.get_json()
    if "name" not in data or "age" not in data:
        return jsonify({"error": "Missing 'name' or 'age'"}), 400
    return jsonify(add_student(data)), 201

@app.route('/students', methods=['GET'])
def get_all():
    return jsonify(get_students()), 200

@app.route('/students/<string:student_id>', methods=['GET'])
def get_by_id(student_id):
    student = get_student_by_id(student_id)
    if student:
        return jsonify(student), 200
    return jsonify({"error": "Student not found"}), 404

@app.route('/students/<string:student_id>', methods=['DELETE'])
def delete(student_id):
    return jsonify(delete_student(student_id)), 200

@app.route('/students/name/<string:name>', methods=['GET'])
def get_by_name(name):
    # Use regex to find students by name
    students = students_collection.find({"name": {"$regex": f".*{name}.*", "$options": "i"}})
    students_list = [{"_id": str(student["_id"]), "name": student["name"], "age": student["age"]} for student in students]
    if students_list:
        return jsonify(students_list), 200
    return jsonify({"error": "No students found with the given name"}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
