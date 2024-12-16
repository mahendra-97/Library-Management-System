from django.utils import timezone
from rest_framework import serializers
from .models import User, Book, BorrowRequest

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8},
        }

    def create(self, validated_data):
        role = validated_data.get('role', 'user')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=role
        )
        return user


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'publisher', 'publication_date', 'isbn']

    def validate_isbn(self, value):
        if len(value) != 13:
            raise serializers.ValidationError("ISBN must be 13 characters long.")
        return value


class BorrowRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BorrowRequest
        fields = ['id', 'book', 'user', 'borrow_date', 'return_date', 'status']
    
    def validate(self, data):
        user = data.get('user')
        if user and not User.objects.filter(id=user.id).exists():
            raise serializers.ValidationError("User does not exist.")
        
        if data['return_date'] <= data['borrow_date']:
            raise serializers.ValidationError("Return date must be after borrow date.")

        if BorrowRequest.objects.filter(book=data['book'], status='approved').exists():
            raise serializers.ValidationError("This book is already borrowed.")
        
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context is required.")
        
        request_user = request.user
        if not isinstance(request_user, User):
            raise serializers.ValidationError("The user is not a valid User instance.")
        validated_data['user'] = request_user
        
        if not request_user.is_active:
            raise serializers.ValidationError("Inactive users cannot make borrow requests.")
        
        return super().create(validated_data)
