from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.contrib.auth import get_user_model
import re

def validate_password_regex(value):
    """
    Requirements: At least 8 characters, one uppercase letter, one lowercase letter, one number, and one special character.
    """
    pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    if not re.match(pattern, value):
        raise ValidationError(
            "Password must be at least 8 characters long and contain an uppercase letter, a lowercase letter, a number, and a special character."
        )
    
class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    role = models.CharField(max_length=10, choices=[('admin', 'Admin'), ('user', 'User')], default='user')

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def update_last_login(self):
        self.last_login = timezone.now()
        self.save()

    class Meta:
        db_table = 'user'

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='library_api_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='library_api_user_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    publication_date = models.DateField()
    isbn = models.CharField(max_length=13, unique=True)
    copies_available = models.IntegerField(default=1)

    class Meta:
        db_table = 'book'
        verbose_name = "Book"
        verbose_name_plural = "Books"

    def __str__(self):
        return self.title


class BookInstance(models.Model):
    book = models.ForeignKey(Book, related_name="instances", on_delete=models.CASCADE)
    is_borrowed = models.BooleanField(default=False)
    borrower = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.book.title} ({'Borrowed' if self.is_borrowed else 'Available'})"


class BorrowRequest(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('approved', 'Approved'), ('denied', 'Denied')]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateField()
    return_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'borrow_request'
        verbose_name = "Borrow Request"
        verbose_name_plural = "Borrow Requests"
        constraints = [
            models.UniqueConstraint(
                fields=['book', 'borrow_date', 'return_date'],
                name='unique_borrow_request'
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"