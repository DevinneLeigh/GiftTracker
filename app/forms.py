from django import forms
from .models import Recipient, Event, WishList, Participant, Budget, Gift

class TemplateFormMixin:
    def to_html(self):
        return self.as_p()

class RecipientForm(TemplateFormMixin, forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ["name"]


class EventForm(TemplateFormMixin, forms.ModelForm):
    class Meta:
        model = Event
        fields = ["event"]

class WishListForm(TemplateFormMixin, forms.ModelForm):
    class Meta:
        model = WishList
        fields = ["item_url"]

class GiftForm(forms.ModelForm):
    class Meta:
        model = Gift
        fields = ["item_url"]
        widgets = {
            "item_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "Product URL"})
        }

class ParticipantForm(forms.ModelForm):
    recipient = forms.ModelChoiceField(
        queryset=Recipient.objects.none(),
        empty_label="Select a recipient",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    budget = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        label="Budget Amount",
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Enter budget"})
    )

    class Meta:
        model = Participant
        fields = ["recipient", "budget"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-fill budget if it exists
        if self.instance and hasattr(self.instance, 'budget'):
            self.fields['budget'].initial = self.instance.budget.price

