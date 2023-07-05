from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import csv 
import io

from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail 
from django_base.settings import EMAIL_HOST_USER

from user_admin.serializers import CourseSerializer, InvitationToCourseAsAdminSerializer
from user_admin.permissions import IsAdmin
from user_admin.models import AdminCourses, InvitationToCourseAsUser, InvitationToCourseAsAdmin, Course
from organization.models import InvitationToBecameUserAdmin,Organization
from organization.serializers import InvitationToBecameUserAdminSerializer

from blockchain.models import TokenGroup
from blockchain.serializers import TokenGroupSerializer

from user_admin.models import Admin


class ResponseInvitationToBecameUserAdminView(APIView):
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
            courses = []
            for course in organization_courses:
                if AdminCourses.objects.filter(admin__user=request.user, course=course).exists() or\
                    (request.user.is_organization and request.user.organization.id == int(organization_id)):
                    courses.append(course)
            serializer = CourseSerializer(courses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Something went wrong', 'e': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data = request.data.copy()
            if not 'organization_id' in data:
                return Response({'error': 'organization_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            organization_id = data.get('organization_id')
            organization = get_object_or_404(Organization, id=organization_id)
            if not Admin.objects.filter(user=request.user, organization=organization).exists():
                return Response({'error': 'You are not allowed to do this'}, status=status.HTTP_403_FORBIDDEN)
            
            data['organization'] = organization_id

            serializer = CourseSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Course created successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Something went wrong', 'e': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
  

class TokenGroupView(APIView):
    permission_classes = (IsAdmin,)

    def get(self, request):
        try:
            if not 'course_id' in request.GET:
                return Response({'error': 'course_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            course_id = request.GET.get('course_id')
            course = get_object_or_404(Course, id=course_id)
            if not (AdminCourses.objects.filter(admin__user=request.user, course=course).exists() or\
                    (request.user.is_organization and request.user.organization == course.organization)):
                return Response({'error': 'You are not allowed to do this'}, status=status.HTTP_403_FORBIDDEN)
            
            token_groups = TokenGroup.objects.filter(course=course)
            serializer = TokenGroupSerializer(token_groups, many=True)
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


def send_email_to_users(course_name, is_admin, users_list):
    extra_text = ' as admin' if is_admin else ''
    subject = f'TBAP - Invitation to join course{extra_text}'
    message = f'You have been invited to join a course on {course_name}{extra_text}. Please click the link below to accept the invitation.'
    from_email = EMAIL_HOST_USER
    send_mail(subject, message, from_email, users_list, fail_silently=False)


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
            
        
            send_email_to_users(course.name, True, [admin.user.email])
            InvitationToCourseAsAdmin.objects.create(course=course, admin=admin)
            return Response({'message': 'Invitation sent successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Something went wrong', 'e': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class SendInvitationToJoinCourseAsUser(APIView):
    permission_classes = (IsAdmin,)

    def get_email_list(self, emails_file, posible_columns):
        emails_reader = csv.reader(emails_file)
        headers = next(emails_reader)  # Leer la primera fila (encabezados)
        # Eliminar el carácter '\ufeff' si está presente
        if headers[0].startswith('\ufeff'):
            headers[0] = headers[0][1:]

        # Eliminar comillas adicionales al final de los encabezados y convertirlos a minúsculas
        headers = [header.strip('"').lower() for header in headers]
        # Buscar la columna de correos electrónicos
        email_column_index = None
        for column_name in posible_columns:
            if column_name in headers:
                email_column_index = headers.index(column_name)
                break

        if email_column_index is not None:
            # Recopilar los correos electrónicos de la columna encontrada
            emails = []
            for row in emails_reader:
                if email_column_index < len(row):
                    email = row[email_column_index].strip()
                    if email:  # Ignorar celdas vacías
                        emails.append(email)
            return emails
        else:
            # No se encontró ninguna columna de correos electrónicos
            return []


    def post(self, request):
        try:
            if not 'course_id' in request.data:
                return Response({'error': 'course_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            if not 'email' in request.data and not 'emails' in request.FILES:
                return Response({'error': 'email in body or emails as file are required'}, status=status.HTTP_400_BAD_REQUEST)
            
            course_id = request.data.get('course_id')
            course = get_object_or_404(Course, id=course_id)

            if not AdminCourses.objects.filter(admin__user=request.user, course=course).exists():
                return Response({'error': 'You are not allowed to do this'}, status=status.HTTP_403_FORBIDDEN)
            
            if 'email' in request.data:
                email = request.data.get('email')
            
                if InvitationToCourseAsUser.objects.filter(course=course, email=email).exists():
                    return Response({'error': 'This user already has an invitation'}, status=status.HTTP_400_BAD_REQUEST)
                
                if AdminCourses.objects.filter(admin__user__email=email, course=course).exists():
                    return Response({'error': 'This user is already in the course'}, status=status.HTTP_400_BAD_REQUEST)
                
                approve_emails = [email]
            
            else:
                approve_emails = []
                already_sended_errors = []
                is_already_in_errors = []

                emails_file = request.FILES['emails']
                emails_file = io.TextIOWrapper(emails_file, encoding='utf-8')
                posible_columns = ['emails', 'direccional de correo', 'correo', 'e-mail', 'dirección de correo',
                                   'e_mail', 'email', 'correo electronico', 'email address', 'email_address']
                
                pre_emails = self.get_email_list(emails_file, posible_columns)
                
                for email in pre_emails:
                    if InvitationToCourseAsUser.objects.filter(course=course, email=email).exists():
                        already_sended_errors.append(email)
                        # return Response({'error': 'This user already has an invitation'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    elif AdminCourses.objects.filter(admin__user__email=email, course=course).exists():
                        is_already_in_errors.append(email)
                        # return Response({'error': 'This user is already in the course'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    else:
                        approve_emails.append(email)
                    
                denied_emails = {"already_sended_errors": already_sended_errors, "is_already_in_errors": is_already_in_errors}
                denied_response = {"amount": len(denied_emails['already_sended_errors']) + 
                                            len(denied_emails['is_already_in_errors']),
                                    "emails": denied_emails
                                    }
                            

            
            send_email_to_users(course.name, False, approve_emails)
            for email in approve_emails:
                InvitationToCourseAsUser.objects.create(course=course, email=email)

            response = {'Accepted': {
                                    'amount': len(approve_emails),
                                    'emails': approve_emails
                                    }
                        }
            if "emails" in request.FILES:
                response['Denied'] = denied_response
            return Response(response, status=status.HTTP_200_OK)
                            
        
        except Exception as e:
            return Response({'error': 'Something went wrong', 'e': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class ResponseInvitationToJoinCourseAsAdminView(APIView):
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