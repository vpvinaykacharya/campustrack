from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from database import Base
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum("admin", "teacher", "student"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
class Teacher(Base):
    __tablename__ = "teachers"

    teacher_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True)
    employee_id = Column(String(30), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    phone = Column(String(15))
class Student(Base):
    __tablename__ = "students"

    student_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True)
    class_id = Column(Integer, ForeignKey("classes.class_id"), nullable=False)
    register_number = Column(String(30), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    phone = Column(String(15))
class Course(Base):
    __tablename__ = "courses"

    course_id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String(100), nullable=False)
    course_code = Column(String(20), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
class Class(Base):
    __tablename__ = "classes"

    class_id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.course_id"), nullable=False)
    semester = Column(Integer, nullable=False)
    section = Column(String(20))
    academic_year = Column(String(20))
class Subject(Base):
    __tablename__ = "subjects"

    subject_id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.class_id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.teacher_id"))
    subject_name = Column(String(100), nullable=False)
    subject_code = Column(String(30), nullable=False)

    __table_args__ = (
        UniqueConstraint("class_id", "subject_code"),
    )
class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"

    session_id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.subject_id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.teacher_id"), nullable=False)
    session_date = Column(Date, nullable=False)
    period_number = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "subject_id",
            "session_date",
            "period_number"
        ),
    )
class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    record_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        Integer,
        ForeignKey("attendance_sessions.session_id"),
        nullable=False
    )
    student_id = Column(
        Integer,
        ForeignKey("students.student_id"),
        nullable=False
    )
    status = Column(Enum("P", "A"), nullable=False)

    __table_args__ = (
        UniqueConstraint("session_id", "student_id"),
    )
class CorrectionRequest(Base):
    __tablename__ = "correction_requests"

    request_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(
        Integer,
        ForeignKey("students.student_id"),
        nullable=False
    )
    record_id = Column(
        Integer,
        ForeignKey("attendance_records.record_id"),
        nullable=False
    )
    reason = Column(Text, nullable=False)
    request_status = Column(
        Enum("pending", "approved", "rejected"),
        server_default="pending"
    )
    requested_at = Column(DateTime, server_default=func.now())