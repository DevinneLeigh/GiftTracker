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


class Budget(models.Model):
    participant = models.OneToOneField(Participant, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Budget for {self.participant}"


class Gift(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    purchased = models.BooleanField(default=False)

    def __str__(self):
        return f"Gift: {self.price}"
