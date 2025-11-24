from django import forms
from .models import Recipient, Event

class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ["name"]


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["event"]
