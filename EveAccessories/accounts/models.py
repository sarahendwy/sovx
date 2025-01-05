from django.db import models
from django.contrib.auth.models import AbstractUser

egypt_governorates = [
    "Cairo",
    "Alexandria",
    "Giza",
    "Qalyubia",
    "Port Said",
    "Suez",
    "Dakahlia",
    "Sharkia",
    "Monufia",
    "Gharbia",
    "Kafr El Sheikh",
    "Beheira",
    "Ismailia",
    "Giza",
    "Beni Suef",
    "Fayoum",
    "Minya",
    "Assiut",
    "Sohag",
    "Qena",
    "Luxor",
    "Aswan",
    "Red Sea",
    "New Valley",
    "Matruh",
    "North Sinai",
    "South Sinai"
]


class User(AbstractUser):
    phone = models.CharField(max_length=11, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    birthdate = models.DateField(null=True, blank=True)
    governorate = models.Choices(egypt_governorates)
    city = models.CharField(max_length=50)
    address = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return self.username

    @property
    def full_name(self):
        if self.first_name:
            return self.first_name + " " + self.last_name
        return self.username
