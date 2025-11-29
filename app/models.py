from django.db import models
from django.contrib.auth.models import User


class Recipient(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.CharField(max_length=255)
    def __str__(self):
        return self.event

class Participant(models.Model):
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.recipient.name} - {self.event.event}"

class WishList(models.Model):
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE, related_name="wishlist")
    item_url = models.CharField(max_length=5000, default="")
    product_name = models.CharField(max_length=255, blank=True, null=True)
    product_image = models.CharField(max_length=5000, blank=True, null=True)
    product_price = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Wish: {self.item_url} ({self.recipient.name})"

class Gift(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    wish_list = models.ForeignKey(
        WishList, on_delete=models.SET_NULL, null=True, blank=True
    )
    item_url = models.CharField(max_length=5000, default="")
    product_name = models.CharField(max_length=255, blank=True, null=True)
    product_image = models.CharField(max_length=5000, blank=True, null=True)
    product_price = models.CharField(max_length=50, blank=True, null=True)
    purchased = models.BooleanField(default=False)

    def __str__(self):
        return f"Gift: {self.item_url} ({'Purchased' if self.purchased else 'Not Purchased'})"

class Budget(models.Model):
    participant = models.OneToOneField(Participant, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f"Budget: {self.price} for {self.participant}"



