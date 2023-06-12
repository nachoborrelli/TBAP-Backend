
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils.translation import gettext_lazy as _
from users.serializers import UserProfileSerializer, UserSerializer
# import view
from django.views import View
from django.shortcuts import render
from django_base.settings import CLIENT_ID, CLIENT_SECRET, BASE_URL
import requests
from users.models import User
from users.utils import get_user_email, create_user_without_password

from rest_framework.authtoken.models import Token

class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')
    

class RecepcionOauthView(View):
    def get(self, request):
        print("GET: ", request.GET)
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
            token, created = Token.objects.get_or_create(user=user)
            print (token, created)

            return render(request, 'home.html')




class UserProfileMe(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            profile_serializer = UserProfileSerializer(request.user.user_profile)
            user_serializer = UserSerializer(request.user) 
            return Response({'user':user_serializer.data, 'user_profile':profile_serializer.data})
        else:
            return Response({'data': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    
    def patch(self, request):
        if request.user.is_authenticated:
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
        else:
            return Response({'data': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)


