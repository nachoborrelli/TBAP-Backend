from django.urls import path
from blockchain.views import TokenClaims

urlpatterns = [
    path('tokens/claim', TokenClaims.as_view(), name='rest_token_claims'),
]