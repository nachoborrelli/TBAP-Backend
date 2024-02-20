from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from blockchain import utils, repository

from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q

from user_admin.models import AdminCourses, Course
from user_admin.serializers import TokenUriCourseSerializer
from organization.serializers import TokenUriOrganizationSerializer
from regular_user.models import UserCourses

from blockchain.models import TokenGroup, UserToken, Signature
from blockchain.serializers import BlockchainTokenSerializer, TokenGroupSerializer, \
    TokenGroupSerializerList, SignatureSerializer, UriUserTokenSerializer, \
    UserTokenSerializer, TokenUriRequestSerializer, UserTokenParamsSerializer

class UserTokenView(APIView):
    """
    View to create and list user tokens (you can think of token groups as classes,
    each token group has a list of students who can actualy claim the token on the blockchain)

    get: return all user groups of a course
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            if not request.user.user_profile.wallet_address:
                return Response({'error': 'You must have a wallet address to do this'}, status=status.HTTP_400_BAD_REQUEST)
            serializer= UserTokenParamsSerializer(data=request.GET)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            validated_data = serializer.validated_data
            utils.update_user_tokens_and_signatures_in_db(request.user)

            filter = Q(user=request.user)
            page = serializer.data['page']
            if 'is_claimed' in validated_data:
                is_claimed = validated_data['is_claimed']
                filter &= Q(is_claimed=is_claimed) if is_claimed != None else Q()
            if 'course_id' in validated_data:
                course_id = validated_data['course_id']
                course = get_object_or_404(Course, id=course_id)
                filter &= Q(token_group__course=course)
            user_tokens = UserToken.objects.filter(filter).order_by('-created_at')

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
    def get (self, request):
        """Return pending signatures for the user"""
        pending_signature = Signature.objects.filter(user=request.user, was_used=False).first()
        if pending_signature:
            serializer = SignatureSerializer(pending_signature)
            serializer.instance.pending = True
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({}, status=status.HTTP_200_OK)
        
    def post(self, request):
        pending_signature = Signature.objects.filter(user=request.user, was_used=False).first()
        if pending_signature:
            serializer = SignatureSerializer(pending_signature)
            serializer.instance.pending = True
            return Response(serializer.data, status=status.HTTP_200_OK)
    
        if not 'user_token_id' in request.data:
            return Response({'error': 'user_token_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        user_token_id = request.data.get('user_token_id')
        user_token = get_object_or_404(UserToken, id=user_token_id)

        if user_token.user != request.user:
            return Response({'error': 'You are not allowed to do this'}, status=status.HTTP_403_FORBIDDEN)
        
        if user_token.is_claimed:
            return Response({'error': 'Token already claimed'}, status=status.HTTP_400_BAD_REQUEST)

        organization = user_token.get_organization()
        nonce = utils.get_new_nonce()

        signature_data = {
                    'token_name': user_token.token_group.name,
                    'organization': organization.id,
                    'nonce': nonce,
                    'uri': str(user_token.id)
                    }
        signature_data['signature'] = utils.create_mint_signature(signature_data['token_name'], signature_data['organization'], 
                                                              signature_data['nonce'], signature_data['uri'])
        signature_data['user'] = request.user.id
        signature_data['pending'] = False
    
        serializer = SignatureSerializer(data=signature_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
class TokenURI(APIView):
    def get(self, request, userTokenId):
        request_serializer = TokenUriRequestSerializer(data={'userTokenId': userTokenId})
        if request_serializer.is_valid():
            db_token = UserToken.objects.filter(id=request_serializer.data['userTokenId']).first()
            if not db_token:
                return Response({'Error': f'Token with id {userTokenId} not found'}, status=status.HTTP_404_NOT_FOUND)
            if not db_token.is_claimed:
                if not utils.update_single_token_and_signature_in_bd(db_token):
                    return Response({'Error': f'Token with id {userTokenId} has not been claimed yet'}, status=status.HTTP_400_BAD_REQUEST)
            blockchain_data = repository.get_reward_overview(db_token.tokenId)
            if not blockchain_data:
                return Response({'Error': f'Blockchain Token with id {userTokenId} not found'}, status=status.HTTP_404_NOT_FOUND)
            
            blockchain_data['tokenId']=db_token.tokenId
            uriUserTokenSerializerData=UriUserTokenSerializer(db_token).data
            BlockchainTokenSerializerData=BlockchainTokenSerializer(blockchain_data).data
            CourseSerializerData= TokenUriCourseSerializer(db_token.token_group.course).data
            OrganizationSerializerData=TokenUriOrganizationSerializer(db_token.token_group.course.organization).data
            
            return Response({
                'db_token' : uriUserTokenSerializerData,
                'blockchain_token': BlockchainTokenSerializerData,
                'course': CourseSerializerData,
                'organization': OrganizationSerializerData
                }, status=status.HTTP_200_OK)
        else:
            return Response(request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
