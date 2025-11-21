from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('lms.urls')),
]

# from django.contrib import admin
# from django.urls import path, include
# from .admin import custom_admin_site  # Import your custom admin

# urlpatterns = [
#     path('admin/', custom_admin_site.urls),  # Use custom admin
#     path('', include('lms.urls')),
# ]
