from rest_framework import serializers
from regular_user.models import UserProfile, UserCourses
from user_admin.serializers import CourseSerializer
from blockchain.utils import is_valid_address

def validate_wallet_address(value):
    if not is_valid_address(value):
        raise serializers.ValidationError('Invalid wallet address.')
    return None
    
class UserProfileSerializer(serializers.ModelSerializer):
    wallet_address = serializers.CharField(validators=[validate_wallet_address])
    user_type = serializers.SerializerMethodField()
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ('user',)

    def get_user_type(self, obj):
        if hasattr(obj.user, 'organization'):
            return 'organization'

        if obj.user.admin.exists():
            return 'user_admin'
        
        if obj.user.user_profile:
            return 'regular_user'
        
        return 'unknown'


class UserCoursesSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    class Meta:
        model = UserCourses
        fields = '__all__'
        read_only_fields = ('user', 'course')
