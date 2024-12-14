from rest_framework import serializers
from .models import User, Book, BorrowRequest

# User Serializer for User Model
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8},  # Adding password length validation
        }

    def create(self, validated_data):
        # Ensure that the password is hashed properly
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],  # Hashing happens here automatically
            role=validated_data['role']
        )
        return user


# Book Serializer for Book Model
class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'publisher', 'publication_date', 'isbn']

    # Optionally add custom validation for fields like ISBN, for example:
    def validate_isbn(self, value):
        if len(value) != 13:
            raise serializers.ValidationError("ISBN must be 13 characters long.")
        return value


class BorrowRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BorrowRequest
        fields = ['id', 'book', 'user', 'borrow_date', 'return_date', 'status']

    def validate_user(self, value):
        # Check if the user exists (not just the ID)
        if not User.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("User does not exist.")
        return value

    def create(self, validated_data):
        # Add the current authenticated user explicitly during the save
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

