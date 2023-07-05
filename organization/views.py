from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.core.mail import send_mail 
from django_base.settings import EMAIL_HOST_USER

from rest_framework.permissions import IsAdminUser
from organization.permissions import IsOrganization
from user_admin.permissions import IsAdmin

from organization.models import InvitationToBecameUserAdmin
from organization.models import Organization
from organization.serializers import OrganizationSerializer
from user_admin.models import Admin
from user_admin.serializers import AdminSerializer

from users.models import User
from user_admin.models import Admin
from django_base.utils import get_random_password


from django.shortcuts import get_object_or_404


class CreateOrganization(APIView):
    '''Create an organization'''
    permission_classes = (IsAdminUser,)

    def post(self, request):
        try:
            data = request.data.copy()
            if not "email" in data:
                return Response({'error': 'email is required'}, status=status.HTTP_400_BAD_REQUEST)
            email = data.get('email')
            if User.objects.filter(email=email).exists():
                return Response({'error': 'This email is already in use'}, status=status.HTTP_400_BAD_REQUEST)
            


            serializer = OrganizationSerializer(data=request.data)
            if serializer.is_valid():
                password = get_random_password(length=10)
                user = User.objects.create_user(email=email, username=email, password=password)
                # verify user email
                user.emailaddress_set.create(email=email, primary=True, verified=True)
                user_data = {
                    'email': email,
                    'password': password,
                }
                serializer.save(user=user)
                Admin.objects.create(user=user, organization=serializer.instance)

                return Response({
                                "user": user_data, 
                                "organization":
                                serializer.data}, 
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SendAdminInvitation(APIView):
    '''Create invitations for user_admins to join an organization'''
    permission_classes = (IsOrganization,)

    def post(self, request):
        if not 'email' in request.data:
            return Response({'error': 'email is required'}, status=status.HTTP_400_BAD_REQUEST)
        organization = request.user.organization
        email = request.data.get('email')
        
        if Admin.objects.filter(user__email=email, organization=organization).exists():
            return Response({'error': 'This user is already an admin'}, status=status.HTTP_400_BAD_REQUEST)
        
        if InvitationToBecameUserAdmin.objects.filter(email=email, organization=organization).exists():
            return Response({'error': 'This user already has an invitation'}, status=status.HTTP_400_BAD_REQUEST)
            
        subject = 'TBAP - Invitation to join organization'
        message = f'You have been invited to join an organization on {organization.name}. Please click the link below to accept the invitation.'
        from_email = EMAIL_HOST_USER
        to_list = [email]
        send_mail(subject, message, from_email, to_list, fail_silently=False)
        InvitationToBecameUserAdmin.objects.create(email=email, organization=organization)

        return Response({'success': 'Invitation sent'}, status=status.HTTP_200_OK)


class AdminsOfOrganization(APIView):
    '''Get all admins of an organization'''
    permission_classes = (IsAdmin,)

    def get(self, request):
        if not 'organization_id' in request.query_params:
            return Response({'error': 'organization_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        organization_id = request.query_params.get('organization_id')
        organization = get_object_or_404(Organization, id=organization_id)
        if not Admin.objects.filter(user=request.user, organization=organization).exists():
            return Response({'error': 'You are not an admin of this organization'}, status=status.HTTP_400_BAD_REQUEST)
        
        admins = Admin.objects.filter(organization=organization)
        return Response({'admins': [{'admin_id': admin.id, 'email': admin.user.email} for admin in admins]}, status=status.HTTP_200_OK)