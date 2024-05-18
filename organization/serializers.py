from rest_framework import serializers
from organization.models import Organization, InvitationToBecameUserAdmin


class TokenUriOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['name', 'description', 'logo']

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

class InvitationToBecameUserAdminSerializer(serializers.ModelSerializer):
    organization_name = serializers.SerializerMethodField()
    class Meta:
        model = InvitationToBecameUserAdmin
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

    def get_organization_name(self, obj):
        return obj.organization.name