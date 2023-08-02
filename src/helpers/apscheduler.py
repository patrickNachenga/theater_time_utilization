from apscheduler.schedulers.background import BackgroundScheduler

from src.helpers.utils import create_course_to_moodle, create_group_to_moodle

# Set up the scheduler
scheduler = BackgroundScheduler()

# add required operation on job
scheduler.add_job(create_course_to_moodle, 'interval', seconds=10)
scheduler.add_job(create_group_to_moodle, 'interval', minutes=1)
