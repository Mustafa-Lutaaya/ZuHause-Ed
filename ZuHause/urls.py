from django.contrib import admin
from django.urls import include, path
from django.conf.urls import handler404
from django.shortcuts import render

def custom_404(request, exception):
    return render(request, "404.html", status=404)

urlpatterns = [
    path('', include('ZHed.urls')),
    path('admin/', admin.site.urls),
]


handler404 = custom_404
