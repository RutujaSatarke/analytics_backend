from rest_framework import serializers
from django.contrib.auth import get_user_model
from analytics.models import FeatureClick
from django.contrib.auth.hashers import make_password

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password_confirm', 'age', 'gender']

    def validate(self, data):
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError({
                'password': 'Passwords do not match.'
            })
        
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({
                'username': 'Username already exists.'
            })
        
        if data.get('email') and User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({
                'email': 'Email already exists.'
            })
        
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            age=validated_data.get('age'),
            gender=validated_data.get('gender')
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'age', 'gender', 'created_at']
        read_only_fields = ['id', 'created_at']


class FeatureClickSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)

    class Meta:
        model = FeatureClick
        fields = ['id', 'user', 'feature_name', 'timestamp']
        read_only_fields = ['id', 'user', 'timestamp']

    def validate_feature_name(self, value):
        valid_features = [choice[0] for choice in FeatureClick.FEATURE_CHOICES]
        if value not in valid_features:
            raise serializers.ValidationError(
                f"Invalid feature. Choose from: {', '.join(valid_features)}"
            )
        return value


class AnalyticsFilterSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    age_group = serializers.ChoiceField(
        choices=['<18', '18-40', '>40'],
        required=False,
        allow_null=True
    )
    gender = serializers.ChoiceField(
        choices=['Male', 'Female', 'Other'],
        required=False,
        allow_null=True
    )
    feature_name = serializers.CharField(required=False, allow_null=True)

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError(
                "start_date must be before end_date."
            )
        
        return data