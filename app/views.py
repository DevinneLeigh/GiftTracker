from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import RecipientForm, EventForm
from .models import Recipient, Event, Participant, Gift, Budget
from .utils import get_default_user

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        events = Event.objects.filter(user=request.user)
    else:
        events = []

    return render(request, "index.html", {"events": events})

def add_recipient(request):
    user = get_default_user()

    if request.method == "POST":
        form = RecipientForm(request.POST)
        if form.is_valid():
            recipient = form.save(commit=False)
            recipient.user = user
            recipient.save()
            return redirect("index")

    else:
        form = RecipientForm()

    return render(request, "add_recipient.html", {"form": form})


def add_event(request):
    user = get_default_user()

    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = user
            event.save()
            return redirect("index")

    else:
        form = EventForm()

    return render(request, "add_event.html", {"form": form})


def view_event(request, event_id):
    user = get_default_user()
    event = get_object_or_404(Event, id=event_id, user=user)
    participants = Participant.objects.filter(event=event)

    return render(request, "view_event.html", {
        "event": event,
        "participants": participants,
    })