
from rest_framework.views import APIView
# from rest_framework.response import Response
# django base view
from django.views import View
from django.http import HttpResponse

class CheckResponse(View):
    def get(self, request):
        print("alo")
        print("request: ", request)
        return HttpResponse("alo")