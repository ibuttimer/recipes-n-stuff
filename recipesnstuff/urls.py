"""recipesnstuff URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.views.defaults import (
    page_not_found, server_error, permission_denied, bad_request
)
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from recipesnstuff import settings
from .constants import (
    BASE_APP_NAME, ADMIN_URL, ACCOUNTS_URL, SUMMERNOTE_URL,
    USERS_URL, USER_APP_NAME, PROFILES_APP_NAME, PROFILES_URL,
    SUBSCRIPTION_APP_NAME, SUBSCRIPTIONS_URL, CHECKOUT_URL, CHECKOUT_APP_NAME,
    RECIPES_URL, RECIPES_APP_NAME
)
from .settings import STATIC_URL


urlpatterns = [
    path(ADMIN_URL, admin.site.urls),
    path(SUMMERNOTE_URL, include('django_summernote.urls')),

    # urls_auth precedes allauth so that its urls override allauth's
    path(ACCOUNTS_URL, include(f'{USER_APP_NAME}.urls_auth')),
    path(ACCOUNTS_URL, include('allauth.urls')),
    path(USERS_URL, include(f'{USER_APP_NAME}.urls')),

    path(PROFILES_URL, include(f'{PROFILES_APP_NAME}.urls')),
    path(SUBSCRIPTIONS_URL, include(f'{SUBSCRIPTION_APP_NAME}.urls')),
    path(CHECKOUT_URL, include(f'{CHECKOUT_APP_NAME}.urls')),
    path(RECIPES_URL, include(f'{RECIPES_APP_NAME}.urls')),

    path('', include(f'{BASE_APP_NAME}.root_urls')),
]

if settings.DEBUG and settings.DEVELOPMENT:
    # mount custom error pages on paths for dev
    # based on idea from https://stackoverflow.com/a/57598336/4054609

    def custom_bad_request(request):
        return bad_request(request, None)

    def custom_permission_denied(request):
        return permission_denied(request, None)

    def custom_page_not_found(request):
        return page_not_found(request, None)

    def custom_server_error(request):
        return server_error(request)

    urlpatterns.extend([
        path("400/", custom_bad_request),
        path("403/", custom_permission_denied),
        path("404/", custom_page_not_found),
        path("500/", custom_server_error),
    ])

if settings.DEBUG or settings.DEVELOPMENT:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    # serve the site.webmanifest images
    urlpatterns += static('/', document_root=STATIC_URL)

if settings.DBG_TOOLBAR:
    urlpatterns.append(
        path('__debug__/', include('debug_toolbar.urls'))
    )
