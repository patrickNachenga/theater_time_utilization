from contextlib import contextmanager

import databases
import sqlalchemy
from sqlalchemy import create_engine, event, func
from sqlalchemy.orm import sessionmaker

from src.core.config import settings
from src.models import ExamCoursework, ExamResult, ExamResultSummary

metadata = sqlalchemy.MetaData()
database = databases.Database(settings.DATABASE_URL)
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, expire_on_commit=False, autoflush=False, bind=engine)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


# Define the attach_coursework_listener function
def attach_coursework_listener(registration_number, first_name, middle_name, last_name, gender):
    def coursework_after_insert_or_update(mapper, connection, target):
        with session_scope() as session:
            total_score = session.query(func.sum(ExamCoursework.score)).filter(
                ExamCoursework.student_uid == target.student_uid,ExamCoursework.program_course == target.program_course).scalar()
            exam_result_summary = session.query(ExamResultSummary).filter(
                ExamResultSummary.student_uid == target.student_uid,
                ExamResultSummary.program_course_id == target.program_course.id,
                ExamResultSummary.number_of_sitting == 1).first()
            if exam_result_summary:
                exam_result_summary.cw_score = total_score
            else:
                new_exam_result = ExamResultSummary(
                    student_uid=target.student_uid,
                    registration_number=registration_number,
                    program_course_id=target.program_course.id,
                    number_of_sitting=1,
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name,
                    gender=gender,
                    course_code=target.program_course.course.code,
                    course_name=target.program_course.course.name,
                    cw_score=total_score,
                )
                session.add(new_exam_result)
            session.commit()

    event.listen(ExamCoursework, 'after_insert', coursework_after_insert_or_update)
    event.listen(ExamCoursework, 'after_update', coursework_after_insert_or_update)
