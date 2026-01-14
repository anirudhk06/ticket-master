from celery import shared_task

from db.models import User


@shared_task
def user_activation_email(user_id):
    try:
        user = User.objects.get(pk=user_id)
        subject = (
            f"{user.first_name or user.display_name or user.email} has been activated"
        )

    except:
        pass

    return
