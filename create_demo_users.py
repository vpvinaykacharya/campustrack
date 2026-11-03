from database import SessionLocal
from models import User, Teacher, Student, Subject
from auth import hash_password

# Demo login credentials
TEACHER_USERNAME = "teacher_demo"
TEACHER_PASSWORD = "Teacher@123"

STUDENT_USERNAME = "student_demo"
STUDENT_PASSWORD = "Student@123"

db = SessionLocal()

try:
    # Find existing demo users
    teacher_user = db.query(User).filter(
        User.username == TEACHER_USERNAME
    ).first()

    student_user = db.query(User).filter(
        User.username == STUDENT_USERNAME
    ).first()

    # Create or reset teacher account
    if teacher_user:
        teacher_user.password_hash = hash_password(TEACHER_PASSWORD)
        teacher_user.role = "teacher"
    else:
        teacher_user = User(
            username=TEACHER_USERNAME,
            password_hash=hash_password(TEACHER_PASSWORD),
            role="teacher"
        )
        db.add(teacher_user)
        db.flush()

    # Create or reset student account
    if student_user:
        student_user.password_hash = hash_password(STUDENT_PASSWORD)
        student_user.role = "student"
    else:
        student_user = User(
            username=STUDENT_USERNAME,
            password_hash=hash_password(STUDENT_PASSWORD),
            role="student"
        )
        db.add(student_user)
        db.flush()

    # Find existing profiles
    teacher = db.query(Teacher).filter(
        Teacher.employee_id == "T001"
    ).first()

    student = db.query(Student).filter(
        Student.register_number == "DEMO001"
    ).first()

    if not teacher:
        raise Exception("Teacher profile T001 was not found.")

    if not student:
        raise Exception("Student profile DEMO001 was not found.")

    # Link accounts to profiles
    teacher.user_id = teacher_user.user_id
    student.user_id = student_user.user_id

    # Assign sample subjects to demo teacher
    db.query(Subject).update(
        {Subject.teacher_id: teacher.teacher_id},
        synchronize_session=False
    )

    # Save changes
    db.commit()

    print("\nDemo accounts are ready!")
    print("Teacher username:", TEACHER_USERNAME)
    print("Teacher password:", TEACHER_PASSWORD)
    print("Student username:", STUDENT_USERNAME)
    print("Student password:", STUDENT_PASSWORD)

    print("\nTeacher profile:", teacher.full_name)
    print("Student profile:", student.full_name)

except Exception as e:
    db.rollback()
    print("\nError:", e)

finally:
    db.close()