from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user_admin.serializers import CourseSerializer
from user_admin.permissions import IsAdmin
from user_admin.models import AdminCourses, InvitationToCourse, Course
from organization.models import InvitationToOrganization
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail 
from django_base.settings import EMAIL_HOST_USER



class AcceptAdminInvitation(APIView):
    permission_classes = (IsAdmin,)
    
    def get(self, request):
        try:
            if not 'invitation_id' in request.GET or not 'invitation_status' in request.GET:
                return Response({'error': 'invitation_id and invitation_status are required'}, status=status.HTTP_400_BAD_REQUEST)
            invitation_id = request.GET.get('invitation_id')
            invitation_status = request.GET.get('invitation_status')
            if invitation_status not in ['accepted', 'rejected']:
                return Response({'error': 'invitation_status must be accepted or rejected'}, status=status.HTTP_400_BAD_REQUEST)
            
            invitation = get_object_or_404(InvitationToOrganization, id=invitation_id)

            invitation.status = invitation_status
            invitation.save()

        except Exception as e:
            return Response({'error': 'Something went wrong', 'e': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CourseView(APIView):
    permission_classes = (IsAdmin,)

    def get(self, request):
        try:
            courses = AdminCourses.objects.filter(admin=request.user.admin).values_list('course', flat=True)
            serializer = CourseSerializer(courses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Something went wrong', 'e': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = CourseSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                AdminCourses.objects.create(admin=request.user.admin, course=serializer.instance)
                return Response({'message': 'Course created successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Something went wrong', 'e': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
  

class SendInvitationEmail(APIView):
    permission_classes = (IsAdmin,)

    def post(self, request):
        try:
            if not 'course_id' in request.data or not 'email' in request.data:
                return Response({'error': 'course_id and email are required'}, status=status.HTTP_400_BAD_REQUEST)
            course_id = request.data.get('course_id')
            email = request.data.get('email')
            course = get_object_or_404(Course, id=course_id)
            subject = 'TBAP - Invitation to join course'
            message = f'You have been invited to join a course on {course.name}. Please click the link below to accept the invitation.'
            from_email = EMAIL_HOST_USER
            to_list = [email]
            send_mail(subject, message, from_email, to_list, fail_silently=False)
            InvitationToCourse.objects.create(course=course, email=email)
            return Response({'message': 'Invitation sent successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Something went wrong', 'e': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)