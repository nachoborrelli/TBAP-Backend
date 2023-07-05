from django.urls import path
from blockchain import views

urlpatterns = [
    path('tokens/claim', views.TokenClaims.as_view(), name='rest_token_claims'),
    path('fetch/', views.FetchData.as_view(), name='test_fetch_data'),
    # TODO: implement token uri fetch
    # path('tokens/<int:tokenId>', views.TokenURI.as_view(), name='fetch_token_uri'),
]