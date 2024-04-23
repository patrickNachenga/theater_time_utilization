from apscheduler.schedulers.background import BackgroundScheduler

from src.helpers.utils import create_course_to_moodle, create_group_to_moodle, enroll_staff_to_moodle_course, \
    enroll_student_to_moodle_course, enroll_student_to_moodle_group, enroll_staff_to_moodle_group, \
    unroll_student_to_moodle_course

# Set up the scheduler
scheduler = BackgroundScheduler()

# add required operation on job
# scheduler.add_job(create_course_to_moodle, 'interval', seconds=10)
# scheduler.add_job(create_group_to_moodle, 'interval', seconds=5)
scheduler.add_job(enroll_staff_to_moodle_course, 'interval', seconds=5)
# scheduler.add_job(enroll_student_to_moodle_course, 'interval', seconds=7)
# scheduler.add_job(enroll_student_to_moodle_group, 'interval', seconds=8)
# scheduler.add_job(enroll_staff_to_moodle_group, 'interval', seconds=9)
# scheduler.add_job(unroll_student_to_moodle_course, 'interval', seconds=10)


scheduler.start()
