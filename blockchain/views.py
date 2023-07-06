from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from blockchain import utils, repository, serializers

from django.shortcuts import get_object_or_404

from user_admin.models import AdminCourses, Course
from regular_user.models import UserCourses

from blockchain.models import TokenGroup
from blockchain.serializers import TokenGroupSerializer, TokenGroupSerializerList


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

    def post(self, request):
        try:
            data = request.data.copy()
            if not 'course_id' in data:
                return Response({'error': 'course_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            course_id = data.get('course_id')
            course = get_object_or_404(Course, id=course_id)

            if not (AdminCourses.objects.filter(admin__user=request.user, course=course).exists() or\
                    (request.user.is_organization and request.user.organization == course.organization)):
                return Response({'error': 'You are not allowed to do this'}, status=status.HTTP_403_FORBIDDEN)
            
            data["course"] = course_id
            data["created_by"] = request.user.id
            serializer = TokenGroupSerializer(data=data)
            if serializer.is_valid():
                serializer.save(course=course)
                return Response({
                    'message': 'Token group created successfully',
                    'data': serializer.data
                    }, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            
        except Exception as e:
            return Response({'error': 'Something went wrong', 'e': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TokenClaims(APIView):


    # TODO: return tokens claimable by user
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
        # TODO: 
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
    
class TokenURI(APIView):
    def get(self, request, tokenId):
        serializer = serializers.TokenURIRequestSerializer(data={'tokenId': tokenId})
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
        # response = repository.get_reward_overview(1)
        # response = repository.get_parsed_rewards_data_for_address("0xf1dD71895e49b1563693969de50898197cDF3481")
        # return Response(response)
        # return Response("Only for testing purposes. :)")  