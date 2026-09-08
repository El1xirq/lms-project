import logging
logger = logging.getLogger(__name__)


def send_subscription_email(student_email, course_title, end_date):
   logger.info(f"📧 Email sent to {student_email}: You subscribed to {course_title} until {end_date}")


def send_expiration_reminder_email(email, course_title, end_date):
    logger.info(f"Email sent to {email}: Your subscription to {course_title} expires in {end_date}.")
    