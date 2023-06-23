from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.core.mail import send_mail 
from django_base.settings import EMAIL_HOST_USER

from organization.permissions import IsOrganization

from organization.models import InvitationToOrganization


class SendAdminInvitation(APIView):
    permission_classes = (IsOrganization,)

    def post(self, request):
        if not 'email' in request.data:
            return Response({'error': 'email is required'}, status=status.HTTP_400_BAD_REQUEST)
        organization = request.user.organization
        email = request.data.get('email')
        subject = 'TBAP - Invitation to join organization'
        message = f'You have been invited to join an organization on {organization.name}. Please click the link below to accept the invitation.'
        from_email = EMAIL_HOST_USER
        to_list = [email]
        send_mail(subject, message, from_email, to_list, fail_silently=False)
        InvitationToOrganization.objects.create(email=email, organization=organization)

        return Response({'success': 'Invitation sent'}, status=status.HTTP_200_OK)



        
