# from django.urls import path
# from django.contrib.auth import views as auth_views
# from . import views

# urlpatterns = [
#     path('', views.home, name='home'),
#     path('register/', views.register, name='register'),
#     path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
#     path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
#     path('profile/', views.profile, name='profile'),
#     path('books/', views.book_list, name='book_list'),
#     path('books/<int:book_id>/', views.book_detail, name='book_detail'),
#     path('books/<int:book_id>/borrow/', views.borrow_book, name='borrow_book'),
#     path('transactions/<int:transaction_id>/return/', views.return_book, name='return_book'),
#     path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
# ]


# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.home, name='home'),
#     path('register/', views.register, name='register'),
#     path('login/', views.user_login, name='login'),
#     path('logout/', views.user_logout, name='logout'),
#     path('profile/', views.profile, name='profile'),
#     path('books/', views.book_list, name='book_list'),
#     path('book/<int:book_id>/', views.book_detail, name='book_detail'),
#     path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
#     path('return/<int:transaction_id>/', views.return_book, name='return_book'),
#     path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
# ]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('books/', views.book_list, name='book_list'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('return/<int:transaction_id>/', views.return_book, name='return_book'),
    path('return-all/', views.bulk_return_books, name='bulk_return_books'),  # Optional
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]