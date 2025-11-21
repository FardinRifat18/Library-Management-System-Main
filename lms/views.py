from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Book, Member, Transaction
from .forms import UserRegisterForm, MemberUpdateForm, BookForm
from datetime import date, timedelta

def home(request):
    books = Book.objects.all()[:6]  # Show 6 recent books on homepage
    context = {
        'books': books,
        'total_books': Book.objects.count(),
        'available_books': Book.objects.filter(status='available').count(),
    }
    return render(request, 'home.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create member profile
            membership_id = f"M{user.id:04d}"
            Member.objects.create(
                user=user,
                membership_id=membership_id
            )
            
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')

@login_required
def profile(request):
    member = get_object_or_404(Member, user=request.user)
    
    if request.method == 'POST':
        u_form = MemberUpdateForm(request.POST, instance=member)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        u_form = MemberUpdateForm(instance=member)
    
    # Get current and past transactions
    current_transactions = Transaction.objects.filter(
        member=member, 
        transaction_type='borrow',
        is_returned=False
    )
    
    past_transactions = Transaction.objects.filter(
        member=member
    ).exclude(is_returned=False)
    
    context = {
        'u_form': u_form,
        'member': member,
        'current_transactions': current_transactions,
        'past_transactions': past_transactions,
    }
    
    return render(request, 'profile.html', context)

def book_list(request):
    query = request.GET.get('q')
    genre_filter = request.GET.get('genre')
    
    books = Book.objects.all()
    
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(isbn__icontains=query)
        )
    
    if genre_filter:
        books = books.filter(genre=genre_filter)
    
    context = {
        'books': books,
        'query': query,
        'genre_filter': genre_filter,
    }
    return render(request, 'book_list.html', context)

# def book_detail(request, book_id):
#     book = get_object_or_404(Book, id=book_id)
    
#     # Check if user has borrowed this book
#     user_has_borrowed = False
#     if request.user.is_authenticated:
#         member = get_object_or_404(Member, user=request.user)
#         user_has_borrowed = Transaction.objects.filter(
#             book=book,
#             member=member,
#             transaction_type='borrow',
#             is_returned=False
#         ).exists()
    
#     context = {
#         'book': book,
#         'user_has_borrowed': user_has_borrowed,
#     }
#     return render(request, 'book_detail.html', context)


# def book_detail(request, book_id): NEW

def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    # Check if user has borrowed this book and get the transaction
    user_has_borrowed = False
    current_transaction_id = None
    
    if request.user.is_authenticated:
        try:
            member = get_object_or_404(Member, user=request.user)
            current_borrow = Transaction.objects.filter(
                book=book,
                member=member,
                transaction_type='borrow',
                is_returned=False
            ).first()
            
            if current_borrow:
                user_has_borrowed = True
                current_transaction_id = current_borrow.id
        except Member.DoesNotExist:
            pass
    
    # Calculate statistics (with fallbacks)
    total_borrow_count = getattr(book, 'total_borrow_count', 0)
    popularity_score = getattr(book, 'popularity_score', 0)
    
    context = {
        'book': book,
        'user_has_borrowed': user_has_borrowed,
        'current_transaction_id': current_transaction_id,
        'total_borrow_count': total_borrow_count,
        'popularity_score': popularity_score,
    }
    return render(request, 'book_detail.html', context)


@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    member = get_object_or_404(Member, user=request.user)
    
    # Check if book is available
    if book.available_copies <= 0:
        messages.error(request, 'Sorry, this book is not available for borrowing.')
        return redirect('book_detail', book_id=book_id)
    
    # Check if user already has this book borrowed
    existing_borrow = Transaction.objects.filter(
        book=book,
        member=member,
        transaction_type='borrow',
        is_returned=False
    ).exists()
    
    if existing_borrow:
        messages.error(request, 'You have already borrowed this book.')
        return redirect('book_detail', book_id=book_id)
    
    # Create borrow transaction with due date (14 days from now)
    due_date = date.today() + timedelta(days=14)
    Transaction.objects.create(
        book=book,
        member=member,
        transaction_type='borrow',
        due_date=due_date
    )
    
    # Update book available copies
    book.available_copies -= 1
    if book.available_copies == 0:
        book.status = 'borrowed'
    book.save()
    
    messages.success(request, f'You have successfully borrowed "{book.title}". Due date: {due_date}')
    return redirect('profile')

# @login_required
# def return_book(request, transaction_id):
#     transaction = get_object_or_404(Transaction, id=transaction_id)
    
#     # Verify that the current user owns this transaction
#     if transaction.member.user != request.user:
#         messages.error(request, 'You are not authorized to return this book.')
#         return redirect('profile')
    
#     # Verify the book is not already returned
#     if transaction.is_returned:
#         messages.error(request, 'This book has already been returned.')
#         return redirect('profile')
    
#     # Mark the borrow transaction as returned
#     transaction.is_returned = True
#     transaction.return_date = date.today()
#     transaction.save()
    
#     # Update book available copies
#     book = transaction.book
#     book.available_copies += 1
#     if book.status == 'borrowed':
#         book.status = 'available'
#     book.save()
    
#     # Create return transaction record
#     Transaction.objects.create(
#         book=transaction.book,
#         member=transaction.member,
#         transaction_type='return',
#         related_transaction=transaction
#     )
    
#     messages.success(request, f'You have successfully returned "{transaction.book.title}".')
#     return redirect('profile')

@login_required
def return_book(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    
    # Verify that the current user owns this transaction
    if transaction.member.user != request.user:
        messages.error(request, 'You are not authorized to return this book.')
        return redirect('profile')
    
    # Verify the book is not already returned
    if transaction.is_returned:
        messages.error(request, 'This book has already been returned.')
        return redirect('profile')
    
    # Mark the borrow transaction as returned
    transaction.is_returned = True
    transaction.return_date = date.today()
    transaction.save()
    
    # Update book available copies
    book = transaction.book
    book.available_copies += 1
    if book.status == 'borrowed' and book.available_copies > 0:
        book.status = 'available'
    book.save()
    
    # Create return transaction record (without related_transaction)
    Transaction.objects.create(
        book=transaction.book,
        member=transaction.member,
        transaction_type='return'
    )
    
    messages.success(request, f'You have successfully returned "{transaction.book.title}".')
    return redirect('profile')

# Added bulk return functionality

@login_required
def bulk_return_books(request):
    if request.method == 'POST':
        member = get_object_or_404(Member, user=request.user)
        current_borrows = Transaction.objects.filter(
            member=member,
            transaction_type='borrow',
            is_returned=False
        )
        
        returned_count = 0
        for transaction in current_borrows:
            # Mark as returned
            transaction.is_returned = True
            transaction.return_date = date.today()
            transaction.save()
            
            # Update book
            book = transaction.book
            book.available_copies += 1
            if book.status == 'borrowed' and book.available_copies > 0:
                book.status = 'available'
            book.save()
            
            # Create return record
            Transaction.objects.create(
                book=transaction.book,
                member=transaction.member,
                transaction_type='return'
            )
            
            returned_count += 1
        
        if returned_count > 0:
            messages.success(request, f'Successfully returned {returned_count} books!')
        else:
            messages.info(request, 'No books to return.')
        
        return redirect('profile')
    
    messages.error(request, 'Invalid request method.')
    return redirect('profile')
#


@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'You are not authorized to access this page.')
        return redirect('home')
    
    # Get statistics for dashboard
    total_books = Book.objects.count()
    total_members = Member.objects.count()
    borrowed_books = Transaction.objects.filter(transaction_type='borrow', is_returned=False).count()
    overdue_books = Transaction.objects.filter(
        transaction_type='borrow', 
        is_returned=False,
        due_date__lt=date.today()
    ).count()
    
    recent_transactions = Transaction.objects.all().order_by('-transaction_date')[:10]
    
    context = {
        'total_books': total_books,
        'total_members': total_members,
        'borrowed_books': borrowed_books,
        'overdue_books': overdue_books,
        'recent_transactions': recent_transactions,
    }
    
    return render(request, 'admin_dashboard.html', context)