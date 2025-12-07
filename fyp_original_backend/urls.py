"""
URL configuration for fyp_original_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from core.auth import api as auth_api   
from core.user_settings import api as settings_api
from core.facebookadcopy import api as facebook_ad_api
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", auth_api.urls),
    path("api/settings/", settings_api.urls),
    path("api/facebook-ad/", facebook_ad_api.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
