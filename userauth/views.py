from django.shortcuts import render

from userauth.models import Transactions

from .serializers import RegisterSerializer, TransactionSerializer, UserSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from .models import Transactions
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.forms.models import model_to_dict
from .serializers import MyTokenObtainPairSerializer


class MyObtainTokenPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class TransactionPostView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        request_data = request.data.copy()
        request_data["owner"] = request.user.id
        serializer = TransactionSerializer(data=request_data)
        other_user = request.data["transaction_with"]

        if serializer.is_valid():
            if request.data["transaction_type"] == "borrow":
                other_transaction = Transactions.objects.create(
                    owner=User.objects.get(id=int(other_user)),
                    transaction_with=User.objects.get(id=int(request.user.id)),
                    transaction_type="lend",
                    amount=request.data["amount"],
                    reason=request.data["reason"],
                )
                other_transaction.save()
                serializer.save()

            elif request.data["transaction_type"] == "lend":
                serializer.save()
                other_transaction = Transactions.objects.create(
                    owner=User.objects.get(id=int(other_user)),
                    transaction_with=User.objects.get(id=int(request.user.id)),
                    transaction_type="borrow",
                    amount=request.data["amount"],
                    reason=request.data["reason"],
                )
                other_transaction.save()

            return Response(
                {"status": "success", "result": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"status": "error", "result": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )


class TransactionGetView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        transactions = Transactions.objects.filter(owner=self.request.user.id)
        serializer = TransactionSerializer(transactions, many=True)
        counts = Transactions.objects.filter(owner=self.request.user.id).count()
        return Response(
            {"counts": counts, "data": serializer.data}, status=status.HTTP_200_OK
        )


class TransactionDetailView(generics.CreateAPIView):
    serializer_class = TransactionSerializer

    def patch(self, request, id):
        request_data = request.data.copy()
        transactions = Transactions.objects.filter(id=id).first()
        transactions.transaction_status = True
        transactions.save()

        other_transactions = Transactions.objects.filter(id=id + 1).first()
        other_transactions.transaction_status = True
        other_transactions.save()

        return JsonResponse(
            {
                "data": "Done",
            },
            status=status.HTTP_205_RESET_CONTENT,
        )


class Userview(generics.CreateAPIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        users = User.objects.all().exclude(id=request.user.id)
        serializer = UserSerializer(users, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)
