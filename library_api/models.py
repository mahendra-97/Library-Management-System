from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [('admin', 'Admin'), ('user', 'User')]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    groups = models.ManyToManyField(
        'auth.Group', 
        related_name='library_user_set', 
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', 
        related_name='library_user_permissions_set', 
        blank=True
    )

    class Meta:
        db_table = 'user'
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.username


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    available = models.BooleanField(default=True)

    class Meta:
        db_table = 'book'
        verbose_name = "Book"
        verbose_name_plural = "Books"

    def __str__(self):
        return self.title


class BorrowRequest(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('approved', 'Approved'), ('denied', 'Denied')]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateField()
    return_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

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
