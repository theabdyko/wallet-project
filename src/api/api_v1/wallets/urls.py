"""
Wallet API URL patterns.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from src.api.api_v1.wallets import views

# Create a router and register the ViewSet
router = DefaultRouter()
router.register(r"", views.WalletViewSet, basename="wallets")

app_name = "wallets"

urlpatterns = [
    path("", include(router.urls)),
]
