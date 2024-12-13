from rest_framework import serializers
from .models import User, Book, BorrowRequest

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class BorrowRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BorrowRequest
        fields = '__all__'
