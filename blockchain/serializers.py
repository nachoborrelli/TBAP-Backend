from user_admin.serializers import CourseSerializer
from organization.serializers import OrganizationSerializer
from rest_framework import serializers
from users.serializers import UserSerializer

from blockchain.models import TokenGroup, Signature, UserToken

class TokenGroupSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    class Meta:
        model = TokenGroup
        fields = '__all__'
    

class TokenGroupSerializerList(serializers.ModelSerializer):
    created_by = UserSerializer()
    class Meta:
        model = TokenGroup
        fields = '__all__'


class SignatureSerializer(serializers.ModelSerializer):
    issuerId = serializers.IntegerField(source='organization.id', read_only=True)
    title = serializers.CharField(source='token_name', read_only=True)
    pending = serializers.SerializerMethodField()
    
    class Meta:
        model = Signature
        fields = ['id', 'nonce', 'signature', 'user', 'title', 'issuerId', 'uri', 'organization', 'token_name', 'pending']
    
    def get_pending(self, obj):
        """return value or return False as default"""
        return getattr(obj, 'pending', False)

    def to_representation(self, instance):
        self.fields.pop('organization')
        self.fields.pop('token_name')
        return super().to_representation(instance)
    
    

class UserTokenSerializer(serializers.ModelSerializer):
    token_group = TokenGroupSerializer()
    class Meta:
        model = UserToken
        fields = ["id", "token_group", "is_claimed", "created_at"]


class TokenUriRequestSerializer(serializers.Serializer):
    userTokenId = serializers.IntegerField()

class BlockchainTokenSerializer(serializers.Serializer):
    tokenId = serializers.IntegerField()
    title = serializers.CharField()
    issuerId = serializers.IntegerField()
    createdAt = serializers.IntegerField()
    uri = serializers.CharField()

class UriUserTokenSerializer(serializers.ModelSerializer):
    description= serializers.CharField(source='token_group.description')
    image= serializers.ImageField(source='token_group.image')
    
    class Meta:
        model = UserToken
        fields = ['description', 'image']


class TokenMixedSerializer(serializers.Serializer):
    # token = serializers.SerializerMethodField()
    # course = serializers.SerializerMethodField()
    # organization = serializers.SerializerMethodField()
    blockchain_token = BlockchainTokenSerializer()
    db_token = UriUserTokenSerializer()
    course = CourseSerializer(source='db_token.token_group.course')
    organization = OrganizationSerializer(source='db_token.token_group.course.organization')

# {
    # token: {db_object, blockchain_data}
    # course: {db_object}
    # organization: {db_object}
# }

    # def get_token(self, obj):
    #     # Assuming `obj` is an instance of UserToken
    #     return {
    #         'tokenId': obj.tokenId,
    #         'title': obj.blockchain_data['title'],  # Replace with actual field names
    #         'issuerId': obj.blockchain_data['issuerId'],
    #         'createdAt': obj.blockchain_data['createdAt'],
    #         'uri': obj.blockchain_data['uri'],
    #         'description': obj.token_group.description,
    #         'image': obj.token_group.image.url if obj.token_group.image else None
    #     }

    # def get_course(self, obj):
    #     return {
    #         'name': obj.token_group.course.name,
    #         'description': obj.token_group.course.description
    #     }

    # def get_organization(self, obj):
    #     return {
    #         'name': obj.token_group.course.organization.name,
    #         'description': obj.token_group.course.organization.description,
    #         'logo': obj.token_group.course.organization.logo.url if obj.token_group.course.organization.logo else None
    #     }
