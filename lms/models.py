from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Book(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('reserved', 'Reserved'),
    ]
    
    GENRE_CHOICES = [
        ('fiction', 'Fiction'),
        ('non-fiction', 'Non-Fiction'),
        ('science', 'Science'),
        ('technology', 'Technology'),
        ('history', 'History'),
        ('biography', 'Biography'),
        ('children', 'Children'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True)
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, default='other')
    published_date = models.DateField(null=True, blank=True)
    publisher = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    cover_image = models.ImageField(upload_to='book_covers/', null=True, blank=True)
    
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} by {self.author}"
    
    def save(self, *args, **kwargs):
        if self.available_copies > 0:
            self.status = 'available'
        else:
            self.status = 'borrowed'
        super().save(*args, **kwargs)

class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    membership_id = models.CharField(max_length=10, unique=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    date_joined = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.membership_id})"

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('borrow', 'Borrow'),
        ('return', 'Return'),
    ]
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    transaction_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    fine_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    is_returned = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.member.user.username} - {self.book.title} ({self.transaction_type})"
    
    def save(self, *args, **kwargs):
        # Set due date to 14 days from transaction date for borrow transactions
        if self.transaction_type == 'borrow' and not self.due_date:
            self.due_date = timezone.now().date() + timedelta(days=14)
        
        # Calculate fine if book is returned after due date
        if self.transaction_type == 'return' and not self.is_returned:
            self.is_returned = True
            self.return_date = timezone.now().date()
            
            if self.return_date > self.due_date:
                days_overdue = (self.return_date - self.due_date).days
                self.fine_amount = days_overdue * 1.00  # $1 per day fine
                
            # Update book available copies
            self.book.available_copies += 1
            self.book.save()
        
        # Update book available copies for borrow transactions
        if self.transaction_type == 'borrow' and not self.is_returned:
            if self.book.available_copies > 0:
                self.book.available_copies -= 1
                self.book.save()
        
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        if not self.is_returned and timezone.now().date() > self.due_date:
            return True
        return False