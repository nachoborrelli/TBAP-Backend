from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail 
from django_base.settings import EMAIL_HOST_USER

from user_admin.serializers import CourseSerializer, InvitationToCourseAsAdminSerializer
from user_admin.permissions import IsAdmin
from user_admin.models import AdminCourses, InvitationToCourseAsUser, InvitationToCourseAsAdmin, Course
from organization.models import InvitationToBecameUserAdmin,Organization
from organization.serializers import InvitationToBecameUserAdminSerializer

from user_admin.models import Admin


class AcceptInvitationToBecameUserAdminView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            invitations = InvitationToBecameUserAdmin.objects.filter(email=request.user.email).exclude(status='Accepted')
            serializer = InvitationToBecameUserAdminSerializer(invitations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Something went wrong', 'e': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def post(self, request):
        try:
            if not 'invitation_id' in request.data or not 'invitation_status' in request.data:
                return Response({'error': 'invitation_id and invitation_status are required'}, status=status.HTTP_400_BAD_REQUEST)
            invitation_id = request.data.get('invitation_id')
            invitation = get_object_or_404(InvitationToBecameUserAdmin, id=invitation_id)

            if request.user.email != invitation.email:
                return Response({'error': 'You are not allowed to do this'}, status=status.HTTP_403_FORBIDDEN)
            
            if invitation.status == 'Accepted':
                return Response({'error': 'This invitation was already accepted'}, status=status.HTTP_400_BAD_REQUEST)
            
            invitation_status = request.data.get('invitation_status')
            if invitation_status not in ['Accepted', 'Rejected']:
                return Response({'error': 'invitation_status must be Accepted or Rejected'}, status=status.HTTP_400_BAD_REQUEST)
            
            if invitation_status == 'Accepted':
                Admin.objects.create(user=request.user, organization=invitation.organization)
            
            invitation.status = invitation_status
            invitation.save()
            return Response({'message': 'Invitation updated successfully'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': 'Something went wrong', 'e': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  

class CourseView(APIView):
    permission_classes = (IsAdmin,)

    def get(self, request):
        try:
            if not 'organization_id' in request.GET:
                return Response({'error': 'organization_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            organization_id = request.GET.get('organization_id')
            organization_courses = Course.objects.filter(organization=organization_id)  
            print(organization_courses)
            # Get only courses that the admin is on it
            courses = []
            for course in organization_courses:
                print(course)
                print(AdminCourses.objects.filter(course=course).first().admin.user)
                print(request.user)
                if AdminCourses.objects.filter(admin__user=request.user, course=course).exists():
                    courses.append(course)
            serializer = CourseSerializer(courses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Something went wrong', 'e': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            
            serializer = CourseSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Course created successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Something went wrong', 'e': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
  


class SendInvitationToJoinCourseAsAdmin(APIView):
    permission_classes = (IsAdmin,)

    def post(self, request):
        try:
            if not 'course_id' in request.data or not 'admin_id' in request.data or not 'organization_id' in request.data:
                return Response({'error': 'organization_id, course_id and admin_id are required'}, status=status.HTTP_400_BAD_REQUEST)
            organization_id = request.data.get('organization_id')
            course_id = request.data.get('course_id')
            admin_id = request.data.get('admin_id')
            organization = get_object_or_404(Organization, id=organization_id)
            course = get_object_or_404(Course, id=course_id)
            admin = get_object_or_404(Admin, id=admin_id, organization=organization)

            if not AdminCourses.objects.filter(admin__user=request.user, course=course).exists():
                return Response({'error': 'You are not allowed to do this'}, status=status.HTTP_403_FORBIDDEN)

            if AdminCourses.objects.filter(admin=admin, course=course).exists():
                return Response({'error': 'This user is already an admin'}, status=status.HTTP_400_BAD_REQUEST)

            if InvitationToCourseAsAdmin.objects.filter(course=course, admin=admin).exists():
                return Response({'error': 'This user already has an invitation'}, status=status.HTTP_400_BAD_REQUEST)
            
        
            subject = 'TBAP - Invitation to join course as admin'
            message = f'You have been invited to join a course on {course.name} as admin. Please click the link below to accept the invitation.'
            from_email = EMAIL_HOST_USER
            to_list = [admin.user.email]
            send_mail(subject, message, from_email, to_list, fail_silently=False)
            InvitationToCourseAsAdmin.objects.create(course=course, admin=admin)
            return Response({'message': 'Invitation sent successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Something went wrong', 'e': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        

class SendInvitationToJoinCourseAsUser(APIView):
    permission_classes = (IsAdmin,)

    def post(self, request):
        try:
            if not 'course_id' in request.data or not 'email' in request.data:
                return Response({'error': 'course_id and email are required'}, status=status.HTTP_400_BAD_REQUEST)
            course_id = request.data.get('course_id')
            email = request.data.get('email')
            course = get_object_or_404(Course, id=course_id)

            if not AdminCourses.objects.filter(admin__user=request.user, course=course).exists():
                return Response({'error': 'You are not allowed to do this'}, status=status.HTTP_403_FORBIDDEN)
            
            if InvitationToCourseAsUser.objects.filter(course=course, email=email).exists():
                return Response({'error': 'This user already has an invitation'}, status=status.HTTP_400_BAD_REQUEST)
            
            if AdminCourses.objects.filter(admin__user__email=email, course=course).exists():
                return Response({'error': 'This user is already an admin'}, status=status.HTTP_400_BAD_REQUEST)
            
            subject = 'TBAP - Invitation to join course'
            message = f'You have been invited to join a course on {course.name}. Please click the link below to accept the invitation.'
            from_email = EMAIL_HOST_USER
            to_list = [email]
            send_mail(subject, message, from_email, to_list, fail_silently=False)
            InvitationToCourseAsUser.objects.create(course=course, email=email)
            return Response({'message': 'Invitation sent successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Something went wrong', 'e': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class InvitationToJoinCourseAsAdminView(APIView):
    permission_classes = (IsAdmin,)

    def get(self, request):
        try:
            invitations = InvitationToCourseAsAdmin.objects.filter(admin__user=request.user).exclude(status='Accepted')
            serializer = InvitationToCourseAsAdminSerializer(invitations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Something went wrong', 'e': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            if not 'invitation_id' in request.data or not 'invitation_status' in request.data:
                return Response({'error': 'invitation_id and invitation_status are required'}, status=status.HTTP_400_BAD_REQUEST)
            invitation_id = request.data.get('invitation_id')
            invitation = get_object_or_404(InvitationToCourseAsAdmin, id=invitation_id)
            invitation_status = request.data.get('invitation_status')
            if invitation.admin.user != request.user:
                return Response({'error': 'You are not allowed to do this'}, status=status.HTTP_403_FORBIDDEN)
            
            if invitation_status not in ['Accepted', 'Rejected']:
                return Response({'error': 'Invalid invitation status, must be either Accepted or Rejected'}, status=status.HTTP_400_BAD_REQUEST)
            
            if invitation.status == 'Accepted':
                return Response({'error': 'This invitation has already been accepted'}, status=status.HTTP_400_BAD_REQUEST)

            if invitation_status == 'Accepted':
                AdminCourses.objects.create(admin=invitation.admin, course=invitation.course)

            invitation.status = invitation_status
            invitation.save()

            return Response({'message': 'Response invitation successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Something went wrong', 'e': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)