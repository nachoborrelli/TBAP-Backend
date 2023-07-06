from django.urls import path
from blockchain.views import TokenClaims, TokenURI, TokenGroupView

urlpatterns = [
    path('token/claim', TokenClaims.as_view(), name='rest_token_claims'),
    path('token/<int:tokenId>', TokenURI.as_view(), name='fetch_token_uri'),
    path('token-groups/', TokenGroupView.as_view(), name='rest_token_group'),
    # path('fetch/', views.FetchData.as_view(), name='test_fetch_data'),
]