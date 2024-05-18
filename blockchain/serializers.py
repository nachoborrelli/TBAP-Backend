from user_admin.serializers import CourseSerializer
from organization.serializers import OrganizationSerializer
from rest_framework import serializers
from users.serializers import UserSerializer

from blockchain.models import TokenGroup, Signature, UserToken


class TokenGroupSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source="course.name", read_only=True)
    users = serializers.SerializerMethodField()
    deleteable = serializers.SerializerMethodField()

    class Meta:
        model = TokenGroup
        fields = "__all__"

    def get_users(self, obj):
        users = []
        for user in obj.user_tokens.all():
            users.append(
                {
                    "id": user.id,
                    "user_id": user.user.id,
                    "email": user.user.email,
                    "created_at": user.created_at,
                    "is_claimed": user.is_claimed,
                }
            )
        return users

    def get_deleteable(self, obj):
        return not obj.at_least_one_claimed()


class TokenGroupSerializerList(serializers.ModelSerializer):
    created_by = UserSerializer()
    deleteable = serializers.SerializerMethodField()

    class Meta:
        model = TokenGroup
        fields = "__all__"

    def get_deleteable(self, obj):
        return not obj.at_least_one_claimed()


class SignatureSerializer(serializers.ModelSerializer):
    issuerId = serializers.IntegerField(source="organization.id", read_only=True)
    title = serializers.CharField(source="token_name", read_only=True)
    pending = serializers.SerializerMethodField()

    class Meta:
        model = Signature
        fields = [
            "id",
            "nonce",
            "signature",
            "user",
            "title",
            "issuerId",
            "uri",
            "organization",
            "token_name",
            "pending",
        ]

    def get_pending(self, obj):
        """pending is true if the signature was not used, false otherwise"""
        return not(getattr(obj, 'was_used'))

    def to_representation(self, instance):
        self.fields.pop("organization")
        self.fields.pop("token_name")
        return super().to_representation(instance)


class UserTokenCreatorSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserToken
        fields = ["id", "token_group", "user"]

    def validate(self, attrs):
        if UserToken.objects.filter(
            user=attrs["user"], token_group=attrs["token_group"]
        ).exists():
            raise serializers.ValidationError("User already has this token")
        return super().validate(attrs)


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
    description = serializers.CharField(source="token_group.description")
    image = serializers.ImageField(source="token_group.image")

    class Meta:
        model = UserToken
        fields = ["description", "image"]


class TokenMixedSerializer(serializers.Serializer):
    # token = serializers.SerializerMethodField()
    # course = serializers.SerializerMethodField()
    # organization = serializers.SerializerMethodField()
    blockchain_token = BlockchainTokenSerializer()
    db_token = UriUserTokenSerializer()
    course = CourseSerializer(source="db_token.token_group.course")
    organization = OrganizationSerializer(
        source="db_token.token_group.course.organization"
    )


class UserTokenParamsSerializer(serializers.Serializer):
    is_claimed = serializers.BooleanField(required=False, allow_null=True, default=None)
    course_id = serializers.IntegerField(required=False)
    page = serializers.IntegerField(default=1)
