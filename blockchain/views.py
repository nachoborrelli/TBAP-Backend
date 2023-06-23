from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from blockchain import utils
from regular_user.serializers import UserProfileSerializer



class TokenClaims(APIView):

    #TODO: return tokens claimable by user
    def get(self, request):
        # if request.user.is_authenticated:
        #     return Response({'user':user_serializer.data, 'user_profile':profile_serializer.data})
        # else:
        #     return Response({'data': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        token_data = {
                    'title': 'test_title',
                    'issuerId': 1,
                    'nonce': 1,
                    'uri': 'test_uri'
                    }
        token_data['signature'] = utils.create_mint_signature(token_data['title'], token_data['issuerId'], 
                                                              token_data['nonce'], token_data['uri'])
        token_data['test_signature']= utils.create_test_signature(token_data['issuerId'])
        return Response(token_data)
    
    #POST: claim tokens for user, return signature for minting
    def post(self, request):
        # if request.user.is_authenticated:
        # else:
        #     return Response({'data': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        #TODO: 
        #1. check user auth
        #2. get user profile & tokens
        #3. check if token exists
        #4. DONE - get signature for minting

        #example token_data
        token_data = {
                    'title': 'test_title',
                    'issuerId': 1,
                    'nonce': 1,
                    'uri': 'test_uri'
                    }
        token_data['signature'] = utils.create_mint_signature(token_data['title'], token_data['issuerId'], 
                                                              token_data['nonce'], token_data['uri'])
        return Response(token_data)