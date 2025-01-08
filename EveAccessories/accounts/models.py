from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager

egypt_governorates = [('Cairo', 'Cairo'), ('Alexandria', 'Alexandria'), ('Giza', 'Giza'), ('Qalyubia', 'Qalyubia'),
                      ('Port Said', 'Port Said'), ('Suez', 'Suez'), ('Dakahlia', 'Dakahlia'), ('Sharkia', 'Sharkia'),
                      ('Monufia', 'Monufia'), ('Gharbia', 'Gharbia'), ('Kafr El Sheikh', 'Kafr El Sheikh'),
                      ('Beheira', 'Beheira'), ('Ismailia', 'Ismailia'), ('Giza', 'Giza'), ('Beni Suef', 'Beni Suef'),
                      ('Fayoum', 'Fayoum'), ('Minya', 'Minya'), ('Assiut', 'Assiut'), ('Sohag', 'Sohag'),
                      ('Qena', 'Qena'), ('Luxor', 'Luxor'), ('Aswan', 'Aswan'), ('Red Sea', 'Red Sea'),
                      ('New Valley', 'New Valley'), ('Matruh', 'Matruh'), ('North Sinai', 'North Sinai'),
                      ('South Sinai', 'South Sinai')]


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields['is_superuser'] = True
        extra_fields['is_staff'] = True
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    phone = models.CharField(max_length=11, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    birthdate = models.DateField(null=True, blank=True)
    governorate = models.CharField(choices=egypt_governorates, max_length=25)
    city = models.CharField(max_length=55)
    address = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return self.email

    @property
    def full_name(self):
        if self.first_name:
            return self.first_name + " " + self.last_name

        return self.email
