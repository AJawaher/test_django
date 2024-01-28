from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('ProducerApp.urls')),
    path('consumer/', include('customer.ConsumerProject.ConsumerApp.urls')),

]
