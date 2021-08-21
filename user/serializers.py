from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers

from core.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    """ Serializer for the users object """
    name = serializers.CharField(source='userprofile.name')
    class Meta:
        model = User
        fields = ('id', 'name', 'username', 'email', 'password',)
        read_only_fields = ('id',)
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}, }

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        data = validated_data.pop('userprofile', None)
        user = User.objects.create_user(**validated_data)
        if data:
            UserProfile.objects.create(user=user, name=data['name'])
        return user

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""
    username = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=username,
            password=password
        )
        if not user:
            msg = 'Unable to authenticate with provided credentials'
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs
