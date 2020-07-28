from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email, password=None):  # Add all required fields
        if not email:
            raise ValueError("User must have an email address")
        if not password:
            raise ValueError("User must have a password")
        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password=None):
        user = self.create_user(
            email,
            password=password,
        )
        user.is_staff = True
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None):
        user = self.create_user(
            email,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    ROLE = (
        ('min', 'Ministry'),
        ('con', 'Contractor')
    )

    email = models.EmailField(verbose_name="Email Address", max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(verbose_name='Date Joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='Last Login', auto_now=True)

    auth = models.BooleanField(default=False)
    role = models.CharField(max_length=10, choices=ROLE, default='con')
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    contact_no = models.CharField(verbose_name="Contact Number", max_length=13, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []   # Required for 'createsuperuser'

    objects = UserManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        """For cpanel."""
        self.is_active = (self.is_active is True)
        self.is_staff = (self.is_staff is True)
        self.is_superuser = (self.is_superuser is True)
        self.auth = (self.auth is True)

        super(User, self).save(*args, **kwargs)

    @property
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def get_short_name(self):
        return f'{self.first_name}'

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """Generate a Token everytime a new User registers."""
    if created:
        Token.objects.create(user=instance)
