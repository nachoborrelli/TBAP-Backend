from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from user_admin.models import InvitationToCourseAsUser

from user_admin.serializers import InvitationToCourseAsUserSerializer
from regular_user.models import UserCourses
from regular_user.serializers import UserCoursesSerializer

from django.shortcuts import get_object_or_404



class InvitationToJoinCourseView(APIView):
    """
    get: return all invitations to join a course as a regular user for the current user
    post: accept or reject an invitation to join a course as a regular user
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            invitations = InvitationToCourseAsUser.objects.filter(email=request.user.email).exclude(status='Accepted')\
                            .order_by('status', '-created_at')
            serializer = InvitationToCourseAsUserSerializer(invitations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Something went wrong', 'e': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def post(self, request):
        try:
            if not 'invitation_id' in request.data or not 'invitation_status' in request.data:
                return Response({'error': 'invitation_id and invitation_status are required'}, status=status.HTTP_400_BAD_REQUEST)
            invitation_id = request.data.get('invitation_id')
            invitation = get_object_or_404(InvitationToCourseAsUser, id=invitation_id)

            if request.user.email != invitation.email:
                return Response({'error': 'You are not allowed to do this'}, status=status.HTTP_403_FORBIDDEN)
            
            if invitation.status == 'Accepted':
                return Response({'error': 'This invitation was already accepted'}, status=status.HTTP_400_BAD_REQUEST)
            
            invitation_status = request.data.get('invitation_status')
            if invitation_status not in ['Accepted', 'Rejected']:
                return Response({'error': 'invitation_status must be Accepted or Rejected'}, status=status.HTTP_400_BAD_REQUEST)
            
            if invitation_status == 'Accepted':
                UserCourses.objects.create(user=request.user, course=invitation.course)
            
            invitation.status = invitation_status
            invitation.save()
            return Response({'message': 'Invitation updated successfully'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': 'Something went wrong', 'e': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


            

class UserCoursesView(APIView):
    """
    View to get all courses of the current user
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user_courses = UserCourses.objects.filter(user=request.user)
            serializer = UserCoursesSerializer(user_courses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Something went wrong', 'e': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


