from rest_framework import serializers
from users.serializers import UserSerializer

from blockchain.models import TokenGroup, Signature


class TokenGroupSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = Signature
        fields = ['id', 'nonce', 'signature', 'user', 'title', 'issuerId', 'uri', 'organization', 'token_name']
    
    def to_representation(self, instance):
        self.fields.pop('organization')
        self.fields.pop('token_name')
        return super().to_representation(instance)
    
    