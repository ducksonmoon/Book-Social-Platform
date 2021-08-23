from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from core.models import UserProfile
from utils.validators import validate_username, validate_email, validate_image_extension


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


class ManageUserSerializer(serializers.ModelSerializer):
    """Serializer for manage user profile"""
    username = serializers.CharField(source='user.username')
    email = serializers.CharField(source='user.email')

    class Meta:
        model = UserProfile
        fields = ('id', 'name', 'username', 'email', 'birth_date', 'avatar', 'social_media_username')

    def validate(self, data):
        """Validate user data"""
        # Validate username
        user = data.get('user')
        username = user.get('username')
        if not validate_username(username):
            raise ValidationError('Username is invalid.')

        # Validate email
        email = user.get('email')
        if not validate_email(email):
            raise ValidationError('Email is invalid.')

        # Validate avatar file
        avatar = data.get('avatar')
        if avatar:
            validate_image_extension(avatar.name)
            if avatar.size > 2 * 1024 * 1024:
                raise ValidationError('Avatar file too large ( > 2mb ).')

        return data

    def update(self, instance, validated_data):
        """Update user profile"""
        user_data = validated_data.pop('user', None)
        instance.name = validated_data.get('name', instance.name)
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.social_media_username = validated_data.get('social_media_username', instance.social_media_username)
        instance.birth_date = validated_data.get('birth_date', instance.birth_date)
        if user_data:
            instance.user.username = user_data.get('username', instance.user.username)
            instance.user.email = user_data.get('email', instance.user.email)            
            instance.user.save()
        instance.save()

        return instance

    