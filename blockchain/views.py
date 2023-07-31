from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from blockchain import utils, repository

from django.shortcuts import get_object_or_404

from user_admin.models import AdminCourses, Course
from regular_user.models import UserCourses

from blockchain.models import TokenGroup, NonceTracker, UserToken
from blockchain.serializers import TokenGroupSerializer, TokenGroupSerializerList, TokenURIRequestSerializer


class TokenGroupView(APIView):
    """
    View to create and list token groups (you can think of token groups as classes,
    each token group has a list of students who can actualy claim the token on the blockchain)

    get: return all token groups of a course
            if the user is not admin of the course, return only the token groups that the user is in
    post: create a new token group
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            if not 'course_id' in request.GET:
                return Response({'error': 'course_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            course_id = request.GET.get('course_id')
            course = get_object_or_404(Course, id=course_id)
            token_groups = TokenGroup.objects.filter(course=course)

            if not (AdminCourses.objects.filter(admin__user=request.user, course=course).exists() or\
                    (request.user.is_organization and request.user.organization == course.organization)):
                # return Response({'error': 'You are not allowed to do this'}, status=status.HTTP_403_FORBIDDEN)
                if UserCourses.objects.filter(user=request.user, course=course).exists():
                    token_groups = token_groups.filter(token_group_users__user=request.user)
                else:
                    return Response({'error': 'You are not allowed to do this'}, status=status.HTTP_403_FORBIDDEN)
            
            serializer = TokenGroupSerializerList(token_groups, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Something went wrong', 'e': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def create_masive_user_tokens(self, users, token_group_id):
        userTokens=[]
        for user in users:
            userTokens.append(UserToken(user_id=user, token_id=token_group_id))
        UserToken.objects.bulk_create(userTokens)



    def post(self, request):
        try:
            data = request.data.copy()
            if not 'course_id' in data:
                return Response({'error': 'course_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            if not 'users' in data:
                return Response({'error': 'users is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            course_id = data.get('course_id')
            course = get_object_or_404(Course, id=course_id)

            if not (AdminCourses.objects.filter(admin__user=request.user, course=course).exists() or\
                    (request.user.is_organization and request.user.organization == course.organization)):
                return Response({'error': 'You are not allowed to do this'}, status=status.HTTP_403_FORBIDDEN)
            
            users = data.pop('users')
            if users == 'all':
                users = UserCourses.objects.filter(course=course).values_list('user', flat=True)
            else:
                if not isinstance(users, list):
                    return Response({'error': 'users must be a list or string "all" '}, status=status.HTTP_400_BAD_REQUEST)
                users = list(set(users))
                not_users = []
                for id in users:
                    if not UserCourses.objects.filter(user__id=id, course=course).exists():
                        not_users.append(id)
                if not_users:
                    return Response({'error': f'The following users are not in the course: {not_users}'}, status=status.HTTP_400_BAD_REQUEST)
            
            data["course"] = course_id
            data["created_by"] = request.user.id
            serializer = TokenGroupSerializer(data=data)
            if serializer.is_valid():
                serializer.save(course=course)
                try:
                    self.create_masive_user_tokens(users, serializer.instance.id)
                except Exception as e:
                    serializer.instance.delete()
                    return Response({'error': 'Something went wrong', 'e': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return Response({
                    'message': 'Token group created successfully',
                    'data': serializer.data
                    }, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            
        except Exception as e:
            return Response({'error': 'Something went wrong', 'e': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TokenClaims(APIView):
    permission_classes = (IsAuthenticated,)
    # def get(self, request):
    #     if not 'token_group_id' in request.GET:
    #         return Response({'error': 'token_group_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    #     token_group_id = request.GET.get('token_group_id')
    #     token_group = get_object_or_404(TokenGroup, id=token_group_id)

    #     organization_id = token_group.course.organization.id
    #     nonce_id = utils.get_new_nonce()
    #     token_data = {
    #                 'title': token_group.name,
    #                 'issuerId': organization_id,
    #                 'wallet_address': request.user.user_profile.wallet_address,             #Va o no va?
    #                 'nonce': nonce_id,
    #                 'uri': token_group_id
    #                 }
    #     token_data['signature'] = utils.create_mint_signature(token_data['title'], token_data['issuerId'], 
    #                                                             token_data['wallet_address'],
    #                                                             token_data['nonce'], token_data['uri'])
    #     return Response(token_data)
    
    #POST: claim tokens for user, return signature for minting
    def post(self, request):
        # if request.user.is_authenticated:
        # else:
        #     return Response({'data': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        # TODO: 
        #1. check user auth ✅
        #2. get user profile & tokens
        #3. check if token exists
        #4. DONE - create signature 
        #5. save in bd
        #6. return signature
        token_groups = TokenGroup.objects.filter(user_tokens__user=request.user)

        #example token_data
        token_data = {
                    'name': 'Backend TEST',
                    'issuerId': 1, #Organizaction id
                    'nonce': 1,
                    'uri': 'test_uri'
                    }
        token_data['signature'] = utils.create_mint_signature(token_data['name'], token_data['issuerId'], 
                                                              token_data['nonce'], token_data['uri'])
        return Response(token_data)  
    
class TokenURI(APIView):
    def get(self, request, tokenId):
        serializer = TokenURIRequestSerializer(data={'tokenId': tokenId})
        if serializer.is_valid():
            blockchain_data = repository.get_reward_overview(serializer.data['tokenId'])
            if not blockchain_data:
                return Response({'Error': f'Token with id {tokenId} not found'}, status=status.HTTP_404_NOT_FOUND)
            # TODO: add bd data to response
            return Response(blockchain_data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    
# class FetchData(APIView):
#     def get(self, request):
        # token_id = 1
        # response = repository.get_reward_overview(token_id)
        # response = repository.get_parsed_rewards_data_for_address("0xf1dD71895e49b1563693969de50898197cDF3481")
        # return Response(response)
        # return Response("Only for testing purposes. :)")  