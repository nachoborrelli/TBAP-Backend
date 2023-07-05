from rest_framework import serializers
from users.serializers import UserSerializer

from blockchain.models import TokenGroup


class TokenGroupSerializer(serializers.ModelSerializer):
    created_by = UserSerializer()
    class Meta:
        model = TokenGroup
        fields = '__all__'
    
class TokenURIRequestSerializer(serializers.Serializer):
    tokenId = serializers.IntegerField()