from django.urls import path
from . import views

app_name = "adminpanel"

urlpatterns = [
    path("", views.admin_dashboard, name="dashboard"),
    path("letters/", views.admin_letters, name="letters"),
    path("letters/<int:pk>/", views.admin_letter_detail, name="letter_detail"),
    path("users/", views.admin_users, name="users"),
    path("users/<int:pk>/", views.admin_user_detail, name="user_detail"),
    path("deposits/", views.admin_deposits, name="deposits"),
    path("withdrawals/", views.admin_withdrawals, name="withdrawals"),
    path("kyc/", views.admin_kyc_list, name="kyc_list"),
    path("kyc/<id>/", views.admin_kyc_detail, name="kyc_details"),
]
