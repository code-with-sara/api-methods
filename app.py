from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure PostgreSQL Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:sara12@localhost:5433/students'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define Student Model
class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(40), nullable=False)
    lname = db.Column(db.String(40), nullable=False)
    options = db.Column(db.String(40), nullable=False)

    def __init__(self, fname, lname, options):
        self.fname = fname
        self.lname = lname
        self.options = options

# Create Database Tables
with app.app_context():
    db.create_all()

# Route to render form
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        options = request.form['options']

        # Check if student already exists
        existing_student = Student.query.filter_by(fname=fname, lname=lname).first()
        if existing_student:
            return "Student already exists!", 400  # Return error message

        # Create new student entry
        student = Student(fname, lname, options)
        db.session.add(student)
        db.session.commit()

        return render_template('success.html', fname=fname, lname=lname, options=options)

# ------------- API METHODS ------------- #

# GET all students
@app.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    return jsonify([{"id": s.id, "fname": s.fname, "lname": s.lname, "options": s.options} for s in students])

# GET a specific student by ID
@app.route('/students/<int:id>', methods=['GET'])
def get_student(id):
    student = Student.query.get(id)
    if student:
        return jsonify({"id": student.id, "fname": student.fname, "lname": student.lname, "options": student.options})
    return jsonify({"error": "Student not found"}), 404

# UPDATE a student
@app.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    student = Student.query.get(id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    data = request.json  # JSON input from request body
    student.fname = data.get('fname', student.fname)
    student.lname = data.get('lname', student.lname)
    student.options = data.get('options', student.options)

    db.session.commit()
    return jsonify({"message": "Student updated successfully", "student": {"id": student.id, "fname": student.fname, "lname": student.lname, "options": student.options}})

# DELETE a student
@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    student = Student.query.get(id)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "Student deleted successfully"})

# ------------------------------------------- #

if __name__ == '__main__':
    app.run(debug=True)
