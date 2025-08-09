"""
API v1 URL configuration.
"""
from django.urls import include, path

app_name = "api"

urlpatterns = [
    path("wallets/", include("src.api.api_v1.wallets.urls", namespace="wallets")),
    path(
        "transactions/",
        include("src.api.api_v1.transactions.urls", namespace="transactions"),
    ),
]
