from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from blockchain import utils, repository



class TokenClaims(APIView):

    #TODO: return tokens claimable by user
    def get(self, request):
        # if request.user.is_authenticated:
        #     return Response({'user':user_serializer.data, 'user_profile':profile_serializer.data})
        # else:
        #     return Response({'data': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        token_data = {
                    'title': 'Backend TEST',
                    'issuerId': 1,
                    'nonce': 1,
                    'uri': 'test_uri'
                    }
        token_data['signature'] = utils.create_mint_signature(token_data['title'], token_data['issuerId'], 
                                                              token_data['nonce'], token_data['uri'])
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
        #4. DONE - create signature 
        #5. save in bd
        #6. return signature

        #example token_data
        token_data = {
                    'title': 'Backend TEST',
                    'issuerId': 1,
                    'nonce': 1,
                    'uri': 'test_uri'
                    }
        token_data['signature'] = utils.create_mint_signature(token_data['title'], token_data['issuerId'], 
                                                              token_data['nonce'], token_data['uri'])
        return Response(token_data)
    
class FetchData(APIView):
    def get(self, request):
        # response = repository.get_reward_overview(1)
        # response = repository.get_parsed_rewards_data_for_address("0xf1dD71895e49b1563693969de50898197cDF3481")
        # return Response(response)
        return Response("Only for testing purposes. :)")