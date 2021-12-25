from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from core.models import UserProfile, ConfirmCode, Invitation
from utils.validators import validate_username, validate_email, validate_image_extension


class UserSerializer(serializers.ModelSerializer):
    """ Serializer for the users object """
    name = serializers.CharField(source='userprofile.name')

    class Meta:
        model = User
        fields = ('id', 'name', 'username', 'email', 'password',)
        read_only_fields = ('id',)
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}, }


    # Custom validation for the username field
    def validate_username(self, value):
        """
        Check if the username is valid and unique
        :param value:
        :return:
        """
        if not validate_username(value):
            raise ValidationError('نام کاربری معتبر نیست')
        elif User.objects.filter(username=value.lower()).exists():
            raise ValidationError('نام کاربری قبلا ثبت شده است')
        return value

    def validate_email(self, value):
        """
        Check if the email is valid and unique
        :param value:
        :return:
        """
        if not validate_email(value):
            raise ValidationError('ایمیل معتبر نیست')
        elif User.objects.filter(email=value.lower()).exists():
            raise ValidationError('ایمیل قبلا ثبت شده است')
        return value

    def create(self, validated_data):
        """Create a new user with encrypted password and return it. """
        data = validated_data.pop('userprofile', None)
        # make username lower case
        validated_data['username'] = validated_data['username'].lower()
        # make email lower case
        validated_data['email'] = validated_data['email'].lower()
        # create user
        user = User.objects.create_user(**validated_data)
        if data:
            userprofile = UserProfile.objects.create(user=user, name=data['name'])
            # Changed our strategy to send an email to the user with a code to confirm their account.
            ''' 
            code = ConfirmCode.objects.create(user=user) 
            send_mail(
                'Nebig - Confirm Code', 
                'Your confirm code is \n\n' + code.code, 
                settings.EMAIL_HOST_USER, 
                [user.email], 
                fail_silently=False
            )
            '''
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
        username = attrs.get('username').lower()
        password = attrs.get('password')

        # If user enter email, find username
        def is_email(username):
            """Check if the username is an email"""
            return '@' in username and '.' in username and 'gmail' in username
        if is_email(username):
            username = User.objects.get(email=username).username

        user = authenticate(
            request=self.context.get('request'),
            username=username,
            password=password
        )
        if not user:
            msg = 'نام کاربری یا کلمه عبور اشتباه است'
            raise ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs


class ManageUserSerializer(serializers.ModelSerializer):
    """Serializer for manage user profile"""
    name = serializers.CharField(source='user.userprofile.name', required=False)
    username = serializers.CharField(source='user.username', required=False)
    email = serializers.CharField(source='user.email', required=False)
    phone_number = serializers.CharField(source='user.userprofile.phone_number', required=False)
    class Meta:
        model = UserProfile
        fields = (
            'id', 
            'name', 
            'username', 
            'email', 
            'birth_date', 
            'avatar', 
            'phone_number',
            'social_media_link'
        )

    def validate_phone_number(self, value):
        """
        Check if the phone number is valid
        :param value:
        :return:
        """
        if not value:
            return value
        # Validate the phone number
        if len(value) != 13:
            print('1--------')
            raise ValidationError('شماره تلفن معتبر نیست')
        elif not value[1:].isdigit():
            print(value[1:])
            print('2--------')
            raise ValidationError('شماره تلفن معتبر نیست')
        return value

    def validate(self, data):
        """Validate user data"""
        # Validate username
        user = data.get('user')
        
        if user:
            username = user.get('username')
            if username:
                if not validate_username(username):
                    raise ValidationError('نام کاربری معتبر نیست')
                if User.objects.filter(username=username).exclude(pk=user.get('id')).exists() and\
                        not self.instance.user.username == username:
                    raise ValidationError('نام کاربری قبلا ثبت شده است')
            # Validate email
            email = user.get('email')
            if email:
                if not validate_email(email):
                    raise ValidationError('ایمیل معتبر نیست')
                if User.objects.filter(email=email).exclude(pk=user.get('id')).exists() and\
                        not self.instance.user.email == email:
                    raise ValidationError('ایمیل قبلا ثبت شده است')
            userprofile = user.get('userprofile')
            if userprofile:
                phone_number = userprofile.get('phone_number')            
                if phone_number:
                    if UserProfile.objects.filter(phone_number=user.get('phone_number')).exclude(pk=user.get('id')).exists() and\
                            not self.instance.user.userproile.phone_number == phone_number:
                        raise ValidationError('شماره تلفن قبلا ثبت شده است')

        # Validate avatar file
        avatar = data.get('avatar')
        if avatar:
            validate_image_extension(avatar.name)
            if avatar.size > 2 * 1024 * 1024:
                raise ValidationError('آواتار باید کمتر از 2 مگابایت باشد')

        return data

    def update(self, instance, validated_data):
        """Update user profile"""
        user_data = validated_data.pop('user', None)
        if validated_data.get('avatar') != None:
            instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.social_media_link = validated_data.get('social_media_link', instance.social_media_link)
        instance.birth_date = validated_data.get('birth_date', instance.birth_date)
        if instance.birth_date == '':
            instance.birth_date = None
        if user_data:
            instance.user.username = user_data.get('username', instance.user.username)
            instance.user.email = user_data.get('email', instance.user.email)            
            user_data = user_data.get('userprofile', None)
            if user_data:
                instance.name = user_data.get('name', instance.name)
                instance.phone_number = user_data.get('phone_number', '')
            instance.user.save()
        instance.save()

        return instance


class ChangePasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class ConfirmCodeSerializer(serializers.Serializer):
    """Serializer for confirm code"""

    email = serializers.EmailField(required=True)
    code = serializers.CharField(max_length=6)
    
    def validate_email(self, value):
        """Validate email"""
        if not User.objects.filter(email=value).exists():
            raise ValidationError('Invalid email.')
        return value        

    def create(self, validated_data):
        """Create a new confirm code"""
        user = User.objects.get(email=validated_data.get('email'))
        try:
            ConfirmCode.objects.get(user=user).delete()
        except ConfirmCode.DoesNotExist:
            code = ConfirmCode.objects.create(user=user)
            send_mail(
                'Nebig - Confirm Code', 
                'Your confirm code is \n\n' + code.code, 
                settings.EMAIL_HOST_USER, 
                [user.email], 
                fail_silently=False
            )
        return code


class InvitationSerializer(serializers.ModelSerializer):
    """Serializer for invitation"""

    class Meta:
        model = Invitation
        fields = ('sender', 'receiver', 'code', 'date_created', 'is_active')
        read_only_fields = ('sender', 'receiver', 'code', 'date_created', 'is_active')


class InvitationCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)
