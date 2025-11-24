from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import RecipientForm, EventForm
from .models import Recipient, Event, Participant, Gift, Budget
from .utils import get_default_user

# Create your views here.
def index(request):
    recipients = Recipient.objects.all()
    events = Event.objects.all()

    return render(request, "index.html", {
        "recipients": recipients,
        "events": events,
    })

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

def edit_recipient(request, id):
    user = get_default_user()
    recipient = get_object_or_404(Recipient, id=id, user=user)

    if request.method == "POST":
        form = RecipientForm(request.POST, instance=recipient)
        if form.is_valid():
            form.save()
            return redirect("index")
    else:
        form = RecipientForm(instance=recipient)

    return render(request, "edit_recipient.html", {"form": form, "recipient": recipient})


def delete_recipient(request, id):
    user = get_default_user()
    recipient = get_object_or_404(Recipient, id=id, user=user)

    if request.method == "POST":  # user confirmed delete
        recipient.delete()
        return redirect("index")

    return render(request, "confirm_delete.html", {
        "object": recipient,
        "type": "Recipient"
    })


def edit_event(request, id):
    user = get_default_user()
    event = get_object_or_404(Event, id=id, user=user)

    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect("index")
    else:
        form = EventForm(instance=event)

    return render(request, "edit_event.html", {"form": form, "event": event})


def delete_event(request, id):
    user = get_default_user()
    event = get_object_or_404(Event, id=id, user=user)

    if request.method == "POST":
        event.delete()
        return redirect("index")

    return render(request, "confirm_delete.html", {
        "object": event,
        "type": "Event"
    })


