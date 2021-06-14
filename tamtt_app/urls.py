# <UrlConfSnippet>
from django.contrib import admin
from django.urls import path, include
from tamtt import views

urlpatterns = [
    path('', include('tamtt.urls')),
    path('admin/', admin.site.urls),
]
# </UrlConfSnippet>
