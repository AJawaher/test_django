from django.contrib import admin
from django.urls import path, include  # Import the 'include' function

urlpatterns = [
    path('admin/', admin.site.urls),
    path('consumer-app/', include('ConsumerApp.urls')),  # Include ConsumerApp URLs
]
