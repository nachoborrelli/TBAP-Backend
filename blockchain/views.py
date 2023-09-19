from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from blockchain import utils, repository

from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator

from user_admin.models import AdminCourses, Course
from regular_user.models import UserCourses

from blockchain.models import TokenGroup, UserToken
from blockchain.serializers import TokenGroupSerializer, TokenGroupSerializerList, SignatureSerializer, UserTokenSerializer, TokenURIRequestSerializer

class UserTokenView(APIView):
    """
    View to create and list user tokens (you can think of token groups as classes,
    each token group has a list of students who can actualy claim the token on the blockchain)

    get: return all user groups of a course
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            course_id = request.GET.get('course_id', None)
            page = request.GET.get('page', 1)
            is_claimed = request.GET.get('is_claimed', True)
            user_tokens = UserToken.objects.filter(user=request.user, is_claimed=is_claimed)
            if course_id:
                course = get_object_or_404(Course, id=course_id)
                user_tokens = user_tokens.filter(token_group__course=course)

            paginator = Paginator(user_tokens, 6)

            serializer = UserTokenSerializer(paginator.page(page), many=True)

            return Response({
                "total_pages": paginator.num_pages,
                "page": page,
                "total_items": paginator.count,
                "data":serializer.data
                },
                status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': 'Something went wrong', 'e': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
                # if UserCourses.objects.filter(user=request.user, course=course).exists():
                #     token_groups = token_groups.filter(token_group_users__user=request.user)
                # else:
                    return Response({'error': 'You are not allowed to do this'}, status=status.HTTP_403_FORBIDDEN)
            
            serializer = TokenGroupSerializerList(token_groups, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Something went wrong', 'e': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def create_masive_user_tokens(self, users, token_group_id):
        userTokens=[]
        for user in users:
            userTokens.append(UserToken(user_id=user, token_group_id=token_group_id))
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


class TokenGroupDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            token_group_id = pk
            token_group = get_object_or_404(TokenGroup, id=token_group_id)
            if not (AdminCourses.objects.filter(admin__user=request.user, course=token_group.course).exists() or\
                    (request.user.is_organization and request.user.organization == token_group.course.organization)):
                if UserCourses.objects.filter(user=request.user, course=token_group.course).exists():
                    if not token_group.token_group_users.filter(user=request.user).exists():
                        return Response({'error': 'You are not allowed to do this'}, status=status.HTTP_403_FORBIDDEN)
                else:
                    return Response({'error': 'You are not allowed to do this'}, status=status.HTTP_403_FORBIDDEN)
            
            serializer = TokenGroupSerializer(token_group)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Something went wrong', 'e': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TokenClaims(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if not 'user_token_id' in request.data:
            return Response({'error': 'user_token_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        user_token_id = request.data.get('user_token_id')
        user_token = get_object_or_404(UserToken, id=user_token_id)

        if user_token.user != request.user:
            return Response({'error': 'You are not allowed to do this'}, status=status.HTTP_403_FORBIDDEN)
        
        if user_token.is_claimed:
            return Response({'error': 'Token already claimed'}, status=status.HTTP_400_BAD_REQUEST)

        token_name = user_token.token_group.name
        organization = user_token.get_organization()
        # uri = f'/token-groups/{user_token.token_group.id}/'
        uri = f'/{user_token.id}/'
        nonce = utils.get_new_nonce()

        #example token_data
        token_data = {
                    'token_name': token_name,
                    'organization': organization.id,
                    'nonce': nonce,
                    'uri': uri
                    }
        
        #obtener datos de la bd
        token_data['signature'] = utils.create_mint_signature(token_data['token_name'], token_data['organization'], 
                                                              token_data['nonce'], token_data['uri'])
        
        token_data['user'] = request.user.id
        
        serializer = SignatureSerializer(data=token_data)
        if serializer.is_valid():
            serializer.save()
            user_token.is_claimed = True
            user_token.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
class TokenURI(APIView):
    def get(self, request, tokenId):
        serializer = TokenURIRequestSerializer(data={'tokenId': tokenId})
        if serializer.is_valid():
            blockchain_data = repository.get_reward_overview(serializer.data['tokenId'])
            if not blockchain_data:
                return Response({'Error': f'Token with id {tokenId} not found'}, status=status.HTTP_404_NOT_FOUND)
            # TODO: add bd data to response
            # UserToken.objects.filter(id=tokenId)
            # obtain token_group data
            # obtain course data
            # obtain organization data
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