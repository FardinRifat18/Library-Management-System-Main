from django.contrib import admin
from .models import Book, Member, Transaction

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'genre', 'status', 'available_copies', 'total_copies']
    list_filter = ['genre', 'status']
    search_fields = ['title', 'author', 'isbn']

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'membership_id', 'phone', 'date_joined']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'membership_id']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['book', 'member', 'transaction_type', 'transaction_date', 'due_date', 'is_returned', 'fine_amount']
    list_filter = ['transaction_type', 'is_returned']
    search_fields = ['book__title', 'member__user__username']