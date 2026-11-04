from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy import text
from sqlalchemy.orm import Session

from database import engine, SessionLocal, Base
from models import (
    User,
    Student,
    Subject,
    Teacher,
    AttendanceSession,
    AttendanceRecord
)

from auth import verify_password

from datetime import date
import os
from dotenv import load_dotenv


load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CampusTrack")


app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY")
)


# Static files and HTML templates
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )


# --------------------------------------------------
# DATABASE TEST
# --------------------------------------------------

@app.get("/test-db")
def test_database():
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT DATABASE()")
        ).scalar()

    return {
        "message": "Database connected successfully!",
        "database": result
    }


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "CampusTrack is running"
    }


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == username
    ).first()

    if not user or not verify_password(
        password,
        user.password_hash
    ):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "error": "Invalid username or password"
            }
        )

    request.session["user_id"] = user.user_id
    request.session["role"] = user.role

    if user.role == "teacher":
        return RedirectResponse(
            url="/teacher",
            status_code=303
        )

    elif user.role == "student":
        return RedirectResponse(
            url="/student",
            status_code=303
        )

    else:
        return RedirectResponse(
            url="/admin",
            status_code=303
        )


# --------------------------------------------------
# TEACHER DASHBOARD
# --------------------------------------------------

@app.get("/teacher")
def teacher_dashboard(request: Request):
    if request.session.get("role") != "teacher":
        return RedirectResponse(
            url="/",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="teacher.html",
        context={}
    )


# --------------------------------------------------
# STUDENT DASHBOARD
# --------------------------------------------------

@app.get("/student")
def student_dashboard(request: Request):
    if request.session.get("role") != "student":
        return RedirectResponse(
            url="/",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="student.html",
        context={}
    )


# --------------------------------------------------
# ADMIN DASHBOARD
# --------------------------------------------------

@app.get("/admin")
def admin_dashboard(request: Request):
    if request.session.get("role") != "admin":
        return RedirectResponse(
            url="/",
            status_code=303
        )

    return {
        "message": "Admin dashboard coming soon"
    }


# --------------------------------------------------
# TAKE ATTENDANCE PAGE
# --------------------------------------------------

@app.get("/take-attendance")
def take_attendance_page(
    request: Request,
    db: Session = Depends(get_db)
):
    if request.session.get("role") != "teacher":
        return RedirectResponse(
            url="/",
            status_code=303
        )

    teacher_user_id = request.session.get("user_id")

    teacher = db.query(Teacher).filter(
        Teacher.user_id == teacher_user_id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found."
        )

    # Demo class students
    students = db.query(Student).filter(
        Student.class_id == 1
    ).order_by(
        Student.register_number
    ).all()

    # Subjects assigned to the logged-in teacher
    subjects = db.query(Subject).filter(
        Subject.teacher_id == teacher.teacher_id
    ).order_by(
        Subject.subject_name
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="take_attendance.html",
        context={
            "students": students,
            "subjects": subjects
        }
    )


# --------------------------------------------------
# SAVE ATTENDANCE
# --------------------------------------------------

@app.post("/save-attendance")
async def save_attendance(
    request: Request,
    subject_id: int = Form(...),
    session_date: date = Form(...),
    period_number: int = Form(...),
    db: Session = Depends(get_db)
):
    if request.session.get("role") != "teacher":
        return RedirectResponse(
            url="/",
            status_code=303
        )

    teacher_user_id = request.session.get("user_id")

    teacher = db.query(Teacher).filter(
        Teacher.user_id == teacher_user_id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found."
        )

    subject = db.query(Subject).filter(
        Subject.subject_id == subject_id
    ).first()

    if not subject:
        raise HTTPException(
            status_code=404,
            detail="Subject not found."
        )

    if subject.teacher_id != teacher.teacher_id:
        raise HTTPException(
            status_code=403,
            detail="You are not assigned to this subject."
        )

    try:
        attendance_session = db.query(
            AttendanceSession
        ).filter(
            AttendanceSession.subject_id == subject_id,
            AttendanceSession.session_date == session_date,
            AttendanceSession.period_number == period_number
        ).first()

        if not attendance_session:
            attendance_session = AttendanceSession(
                subject_id=subject_id,
                teacher_id=teacher.teacher_id,
                session_date=session_date,
                period_number=period_number
            )

            db.add(attendance_session)
            db.flush()

        students = db.query(Student).filter(
            Student.class_id == subject.class_id
        ).all()

        form_data = await request.form()

        for student in students:
            status = form_data.get(
                f"status_{student.student_id}"
            )

            if status not in ["P", "A"]:
                continue

            record = db.query(
                AttendanceRecord
            ).filter(
                AttendanceRecord.session_id
                == attendance_session.session_id,
                AttendanceRecord.student_id
                == student.student_id
            ).first()

            if record:
                record.status = status

            else:
                record = AttendanceRecord(
                    session_id=attendance_session.session_id,
                    student_id=student.student_id,
                    status=status
                )

                db.add(record)

        db.commit()

    except Exception:
        db.rollback()
        raise

    return RedirectResponse(
        url="/teacher",
        status_code=303
    )


# --------------------------------------------------
# ATTENDANCE RECORDS
# --------------------------------------------------

@app.get(
    "/attendance-records",
    response_class=HTMLResponse
)
def attendance_records_page(
    request: Request,
    subject_id: int = None,
    record_date: date = None,
    db: Session = Depends(get_db)
):
    if request.session.get("role") != "teacher":
        return RedirectResponse(
            url="/",
            status_code=303
        )

    teacher_user_id = request.session.get("user_id")

    teacher = db.query(Teacher).filter(
        Teacher.user_id == teacher_user_id
    ).first()

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found."
        )

    query = (
        db.query(
            AttendanceSession,
            Subject,
            AttendanceRecord,
            Student
        )
        .join(
            Subject,
            AttendanceSession.subject_id
            == Subject.subject_id
        )
        .join(
            AttendanceRecord,
            AttendanceSession.session_id
            == AttendanceRecord.session_id
        )
        .join(
            Student,
            AttendanceRecord.student_id
            == Student.student_id
        )
        .filter(
            AttendanceSession.teacher_id
            == teacher.teacher_id
        )
    )

    if subject_id is not None:
        query = query.filter(
            Subject.subject_id == subject_id
        )

    if record_date is not None:
        query = query.filter(
            AttendanceSession.session_date == record_date
        )

    records = query.order_by(
        AttendanceSession.session_date.desc(),
        AttendanceSession.period_number
    ).all()

    subjects = db.query(Subject).filter(
        Subject.teacher_id == teacher.teacher_id
    ).order_by(
        Subject.subject_name
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="attendance_records.html",
        context={
            "records": records,
            "subjects": subjects,
            "selected_subject_id": subject_id,
            "selected_date": record_date
        }
    )