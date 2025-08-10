"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

api_prefix = "api"

api = NinjaAPI()
api.add_router(f"/{api_prefix}", "accounts.api.router")
api.add_router(f"/{api_prefix}", "articles.api.router")
api.add_router(f"/{api_prefix}", "comments.api.router")
api.add_router("/images", "image_server.api.router")
api.add_router("/auth", "jwt_ninja.api.router")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", api.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
