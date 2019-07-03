"""sogangdjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from Home.views import homepage_view
urlpatterns = [
    url(r'^auth/', include('Auth.urls', namespace='auth')),
    url(r'^api/v1/auth/', include('Auth.api.urls', namespace="auth_api")),
    url(r'^profile/', include('Profile.urls', namespace='profile')),
    url(r'^follow/', include('Following.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^posts/', include('Post.urls', namespace='posts')),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'$', homepage_view, name='home'),
]
urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)
