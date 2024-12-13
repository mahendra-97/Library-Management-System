import csv
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Book, BorrowRequest
from .serializers import UserSerializer, BookSerializer, BorrowRequestSerializer

class BooksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
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

            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CreateLibraryUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BorrowRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        borrow_requests = BorrowRequest.objects.all()
        serializer = BorrowRequestSerializer(borrow_requests, many=True)
        return Response(serializer.data)

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

class UserBorrowHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        borrow_requests = BorrowRequest.objects.filter(user_id=user_id)
        serializer = BorrowRequestSerializer(borrow_requests, many=True)
        return Response(serializer.data)


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