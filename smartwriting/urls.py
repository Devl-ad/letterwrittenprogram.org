from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# from two_factor.urls import urlpatterns as tf_urls
from django.contrib.auth import views as auth_views

from apps.dashboard.views import home_page

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "account/login/",
        auth_views.LoginView.as_view(template_name="dashboard/login.html"),
        name="login",
    ),
    path("account/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    path("dashboard/", include("apps.dashboard.urls", namespace="dashboard")),
    path("", home_page, name="home"),
    path("letters/", include("apps.letters.urls", namespace="letters")),
    path("payments/", include("apps.payments.urls", namespace="payments")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
