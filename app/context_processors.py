from .models import Event, Recipient
from .utils import get_default_user

def global_data(request):
    user = request.user if request.user.is_authenticated else get_default_user()

    if user:
        events = Event.objects.filter(user=user)
        recipients = Recipient.objects.filter(user=user)
    else:
        events = Event.objects.none()
        recipients = Recipient.objects.none()

    return {
        "all_events": events,
        "all_recipients": recipients,
    }
