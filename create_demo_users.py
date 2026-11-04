from database import SessionLocal
from models import User, Teacher, Student, Subject
from auth import hash_password


# Demo login credentials
TEACHER_USERNAME = "teacher_demo"
TEACHER_PASSWORD = "Teacher@123"

STUDENT_USERNAME = "student_demo"
STUDENT_PASSWORD = "Student@123"


def create_or_reset_demo_users():
    db = SessionLocal()

    try:
        # Find the demo teacher and student users
        teacher_user = (
            db.query(User)
            .filter(User.username == TEACHER_USERNAME)
            .first()
        )

        student_user = (
            db.query(User)
            .filter(User.username == STUDENT_USERNAME)
            .first()
        )

        # Create teacher user if it doesn't exist
        if not teacher_user:
            teacher_user = User(
                username=TEACHER_USERNAME,
                password_hash=hash_password(TEACHER_PASSWORD),
                role="teacher"
            )
            db.add(teacher_user)
            db.flush()
        else:
            teacher_user.password_hash = hash_password(TEACHER_PASSWORD)
            teacher_user.role = "teacher"

        # Create student user if it doesn't exist
        if not student_user:
            student_user = User(
                username=STUDENT_USERNAME,
                password_hash=hash_password(STUDENT_PASSWORD),
                role="student"
            )
            db.add(student_user)
            db.flush()
        else:
            student_user.password_hash = hash_password(STUDENT_PASSWORD)
            student_user.role = "student"

        # Find the existing teacher and student profiles
        teacher = (
            db.query(Teacher)
            .filter(Teacher.employee_id == "T001")
            .first()
        )

        student = (
            db.query(Student)
            .filter(Student.register_number == "DEMO001")
            .first()
        )

        if not teacher:
            raise Exception(
                "Teacher profile T001 was not found in the database."
            )

        if not student:
            raise Exception(
                "Student profile DEMO001 was not found in the database."
            )

        # Link user accounts to their profiles
        teacher.user_id = teacher_user.user_id
        student.user_id = student_user.user_id

        # Assign existing subjects to the demo teacher
        db.query(Subject).update(
            {Subject.teacher_id: teacher.teacher_id},
            synchronize_session=False
        )

        db.commit()

        print("\nDemo accounts created/reset successfully!")
        print("-----------------------------------------")
        print("Teacher username:", TEACHER_USERNAME)
        print("Teacher password:", TEACHER_PASSWORD)
        print("-----------------------------------------")
        print("Student username:", STUDENT_USERNAME)
        print("Student password:", STUDENT_PASSWORD)
        print("-----------------------------------------")

    except Exception as error:
        db.rollback()
        print("\nError:", error)

    finally:
        db.close()


if __name__ == "__main__":
    create_or_reset_demo_users()