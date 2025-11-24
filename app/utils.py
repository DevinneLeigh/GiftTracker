from django.contrib.auth.models import User

def get_default_user():
    user, created = User.objects.get_or_create(
        username="default_user",
        defaults={"password": "!"},  # unusable password
    )
    return user
