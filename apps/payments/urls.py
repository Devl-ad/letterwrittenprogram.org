from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("deposit/", views.deposit_view, name="deposit"),
    path("withdrawal/", views.withdrawal_view, name="withdrawal"),
    path("transactions/", views.transactions_view, name="transactions"),
]
