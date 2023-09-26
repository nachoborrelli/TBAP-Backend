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

    
class TokenURIRequestSerializer(serializers.Serializer):
    tokenId = serializers.IntegerField()


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

