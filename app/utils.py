from django.contrib.auth.models import User
from decimal import Decimal
from app.scraper import Scraper

def get_default_user():
    user, created = User.objects.get_or_create(
        username="default_user",
        defaults={"password": "!"},  # unusable password
    )
    return user

def compute_totals(participants):
    for p in participants:
        total_spent = sum(Decimal(gift.product_price or 0) for gift in p.gift_set.all())
        budget_amount = Decimal(p.budget.price) if hasattr(p, "budget") and p.budget else Decimal('0')
        p.spent = total_spent
        p.remaining = budget_amount - total_spent
    return participants



s = Scraper("https://target.com")