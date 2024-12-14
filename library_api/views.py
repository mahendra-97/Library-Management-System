import csv
import traceback
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Book, BorrowRequest, User
from .serializers import UserSerializer, BookSerializer, BorrowRequestSerializer
import logging

logger = logging.getLogger(__name__)

# View for creating a book (for librarian)
class CreateBookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View for listing books (for users and librarians)
class BooksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BorrowRequestSerializer(data=request.data, context={'request': request})  # Pass request context

        if serializer.is_valid():
            book = serializer.validated_data['book']
            borrow_date = serializer.validated_data['borrow_date']
            return_date = serializer.validated_data['return_date']

            # Check for overlapping borrow requests
            if BorrowRequest.objects.filter(
                book=book,
                status='approved',
                borrow_date__lt=return_date,
                return_date__gt=borrow_date
            ).exists():
                return Response({"error": "This book is already borrowed during the requested period."},
                                 status=status.HTTP_400_BAD_REQUEST)

            borrow_request = serializer.save()
            return Response(BorrowRequestSerializer(borrow_request).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# View for handling borrow requests (for users)
class BorrowRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        borrow_requests = BorrowRequest.objects.all()
        serializer = BorrowRequestSerializer(borrow_requests, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = BorrowRequestSerializer(data=request.data)
        if serializer.is_valid():
            book = serializer.validated_data['book']
            borrow_date = serializer.validated_data['borrow_date']
            return_date = serializer.validated_data['return_date']

            # Check for overlapping borrow requests
            if BorrowRequest.objects.filter(
                book=book,
                status='approved',
                borrow_date__lt=return_date,
                return_date__gt=borrow_date
            ).exists():
                return Response({"error": "This book is already borrowed during the requested period."},
                                 status=status.HTTP_400_BAD_REQUEST)

            borrow_request = serializer.save(user=request.user)
            return Response(BorrowRequestSerializer(borrow_request).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            borrow_request = BorrowRequest.objects.get(pk=pk)
        except BorrowRequest.DoesNotExist:
            return Response({"error": "Borrow request not found"}, status=status.HTTP_404_NOT_FOUND)

        status_choice = request.data.get("status")
        if status_choice not in ["approved", "denied"]:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        borrow_request.status = status_choice
        borrow_request.save()
        return Response({"message": f"Borrow request {status_choice} successfully"}, status=status.HTTP_200_OK)


class CreateLibraryUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Ensure the email is unique
            if User.objects.filter(email=request.data.get('email')).exists():
                return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error occurred while creating user: {e}")
            return Response({"error": "An error occurred while creating the user."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserBorrowHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        borrow_requests = BorrowRequest.objects.filter(user_id=user_id)
        serializer = BorrowRequestSerializer(borrow_requests, many=True)
        return Response(serializer.data)


# View for personal borrow history (for users)
class PersonalBorrowHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        borrow_requests = BorrowRequest.objects.filter(user=request.user)
        serializer = BorrowRequestSerializer(borrow_requests, many=True)
        return Response(serializer.data)


class DownloadBorrowHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        borrow_requests = BorrowRequest.objects.filter(user=request.user)

        if not borrow_requests:
            return Response({"error": "No borrow history found for this user."}, status=status.HTTP_404_NOT_FOUND)

        # Create the HttpResponse object with CSV header
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="borrow_history.csv"'

        writer = csv.writer(response)
        writer.writerow(['Book Title', 'Borrow Date', 'Return Date', 'Status'])

        for request in borrow_requests:
            writer.writerow([
                request.book.title,
                request.borrow_date,
                request.return_date,
                request.status
            ])

        return response

