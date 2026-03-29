from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),   # ✅ ADD THIS
    path('api/', include('api.urls')),
]