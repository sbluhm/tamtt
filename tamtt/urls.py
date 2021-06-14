# <UrlConfSnippet>
from django.contrib import admin
from django.urls import path, include
from tutorial import views

urlpatterns = [
    path('', include('tutorial.urls')),
    path('admin/', admin.site.urls),
]
# </UrlConfSnippet>
