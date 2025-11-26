from django import forms
from .models import Recipient, Event, WishList

class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ["name"]


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["event"]

class WishListForm(forms.ModelForm):
    class Meta:
        model = WishList
        fields = ["item_url"]
