from datetime import timedelta
from random import randint

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import PermissionsMixin
from django.db.models import ForeignKey, Model, CASCADE, Index
from django.db.models.fields import (
    EmailField,
    CharField,
    DateTimeField,
    BooleanField,
    TextField,
)
from django.utils.timezone import now

from core.managers import CustomUserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = EmailField(max_length=255, unique=True)
    first_name = CharField(max_length=255, blank=True, null=True)
    last_name = CharField(max_length=255, blank=True, null=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    verified_at = DateTimeField(blank=True, null=True)

    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"


class Deck(Model):
    creator = ForeignKey(
        User, on_delete=CASCADE, related_name="creator", db_column="creator_id"
    )
    name = CharField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        db_table = "decks"


class Card(Model):
    deck = ForeignKey(Deck, on_delete=CASCADE, related_name="deck", db_column="deck_id")
    question = TextField()
    answer = TextField()
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        db_table = "cards"
        indexes = [Index(fields=["deck"])]


class ReviewLog(Model):
    card = ForeignKey(
        Card, on_delete=CASCADE, related_name="review_logs", db_column="card_id"
    )
    user = ForeignKey(
        User, on_delete=CASCADE, related_name="review_logs", db_column="user_id"
    )
    response = TextField()
    reviewed_at = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "review_logs"
        indexes = [Index(fields=["card"])]


class Otp(Model):
    user = ForeignKey(User, on_delete=CASCADE, related_name="otp", db_column="user_id")
    otp_hash = TextField()
    issued_at = DateTimeField(auto_now_add=True)
    intent = CharField(max_length=50, default="registration")

    class Meta:
        db_table = "otps"

    @classmethod
    def generate_for_user(cls, user, intent="registration"):
        buffer_time = now() - timedelta(minutes=5)

        existing_otp = cls.objects.filter(
            user=user, intent=intent, issued_at__gt=buffer_time
        ).last()
        if existing_otp:
            existing_otp.delete()

        plain_otp = str(randint(100000, 999999))
        cls.objects.create(user=user, intent=intent, otp_hash=make_password(plain_otp))
        return plain_otp
