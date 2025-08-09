"""
Transaction API URL patterns.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from src.api.api_v1.transactions import views

# Create a router and register the ViewSet
router = DefaultRouter()
router.register(r"", views.TransactionViewSet, basename="transactions")

app_name = "transactions"

urlpatterns = [
    path("", include(router.urls)),
]
