from getpass import getpass

from database import SessionLocal
from models import User, Teacher, Student, Subject
from auth import hash_password


db = SessionLocal()

try:
    # Find existing demo accounts
    teacher_user = db.query(User).filter(
        User.username == "teacher_demo"
    ).first()

    student_user = db.query(User).filter(
        User.username == "student_demo"
    ).first()

    # Create the demo teacher account if it does not exist
    if not teacher_user:
        teacher_password = getpass("Set demo teacher password: ")

        teacher_user = User(
            username="teacher_demo",
            password_hash=hash_password(teacher_password),
            role="teacher"
        )

        db.add(teacher_user)
        db.flush()

    # Create the demo student account if it does not exist
    if not student_user:
        student_password = getpass("Set demo student password: ")

        student_user = User(
            username="student_demo",
            password_hash=hash_password(student_password),
            role="student"
        )

        db.add(student_user)
        db.flush()

    # Find the existing teacher and student profiles
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

    # Link accounts to their profiles
    teacher.user_id = teacher_user.user_id
    student.user_id = student_user.user_id

    # Assign the demo teacher to all sample subjects
    db.query(Subject).update(
        {Subject.teacher_id: teacher.teacher_id},
        synchronize_session=False
    )

    # Save changes
    db.commit()

    print("\nDemo accounts are ready!")
    print("Teacher username: teacher_demo")
    print("Student username: student_demo")

    # Display teacher profile
    print("\n--- Teacher Profile ---")
    print(
        "Teacher ID:",
        teacher.teacher_id,
        "| Employee ID:",
        teacher.employee_id,
        "| Name:",
        teacher.full_name
    )

    # Display subject assignments
    print("\n--- Subject Assignments ---")

    subjects = db.query(Subject).all()

    for subject in subjects:
        print(
            "Subject ID:",
            subject.subject_id,
            "| Subject:",
            subject.subject_name,
            "| Assigned Teacher ID:",
            subject.teacher_id
        )

except Exception as e:
    db.rollback()
    print("\nError:", e)

finally:
    db.close()