
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils.translation import gettext_lazy as _
from users.serializers import UserSerializer
from regular_user.serializers import UserProfileSerializer
from django.views import View
from django.shortcuts import render
from django_base.settings import CLIENT_ID, CLIENT_SECRET
import requests
from users.models import User
from users.utils import get_user_email, create_user_without_password

from rest_framework.authtoken.models import Token

class LoginView(View):
    """
    Login view, this is just for TEST, this view should be in the frontend
    """
    def get(self, request):
        return render(request, 'login.html')
    

class RecepcionOauthView(View):
    def get(self, request):
        if 'code' in request.GET:
            code = request.GET.get('code') 
            url = 'https://127.0.0.1:8001/o/token/'
            # print("URL: ", f'{BASE_URL}/api/users/oauth/')
            data = {
                'code': code,
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                # 'redirect_uri': f'{BASE_URL}/api/users/oauth/',
                'redirect_uri': 'https://localhost:8000/api/users/oauth/',
                'grant_type': 'authorization_code'
            }
            r = requests.post(url, data=data, verify=False)
            email = get_user_email(r.json()['access_token'])
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
            else:
                user = create_user_without_password(email)
            
            # login
            token, created = Token.objects.get_or_create(user=user)     # access token
            print (token, created)

            return render(request, 'home.html')


class UserProfileMe(APIView):
    """
    View to get user and user profile data from the current user
    get: return user and user profile data
    patch: update user and user profile data
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile_serializer = UserProfileSerializer(request.user.user_profile)
        user_serializer = UserSerializer(request.user) 
        return Response({'user':user_serializer.data, 'user_profile':profile_serializer.data})
    
    def patch(self, request):
        user_serializer = UserSerializer(data=request.data, instance=request.user, partial=True)
        if user_serializer.is_valid():
            profile_serializer = UserProfileSerializer(data=request.data, instance=request.user.user_profile, partial=True)
            if profile_serializer.is_valid():
                user_serializer.save()
                profile_serializer.save()

                return Response({'user':user_serializer.data, 'user_profile':profile_serializer.data})
    
            else:
                return Response(profile_serializer.errors)
        else:
            return Response(user_serializer.errors)


