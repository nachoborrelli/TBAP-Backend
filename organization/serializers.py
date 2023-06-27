from rest_framework import serializers
from organization.models import Organization, InvitationToBecameUserAdmin


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

class InvitationToBecameUserAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvitationToBecameUserAdmin
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

