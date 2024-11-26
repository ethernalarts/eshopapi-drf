from datetime import datetime, timedelta

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from account.serializers import UserSerializer, SignUpSerializer

from utils.helpers import get_current_host


# Create your views here.

@api_view(['POST'])
def register(request):
    data = request.data
    user = SignUpSerializer(data=data)

    if not user.is_valid():
        return Response(user.errors)
    if not User.objects.filter(username=data['email']).exists():
        user = User.objects.create(
            first_name = data['first_name'],
            last_name = data['last_name'],
            email = data['email'],
            username = data['email'],
            password = make_password(data['password'])
        )

        return Response('User has been registered', status=status.HTTP_201_CREATED)
    else:
        return Response('User already exists', status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    user = UserSerializer(request.user)
    return Response(user.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request):
    user = request.user
    data = request.data

    user.first_name = data['first_name']
    user.last_name = data['last_name']
    user.email = data['email']
    user.username = data['email']

    if data['password'] != "":
        user.password = make_password(data['password'])

    user.save()

    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)


@api_view(['POST'])
def forgot_password(request):
    data = request.data
    user = get_object_or_404(User, email=data['email'])
    token = get_random_string(50)
    expiry_date = datetime.now() + timedelta(minutes=30)

    user.profile.username = user.username
    user.profile.reset_password_token = token
    user.profile.reset_password_expires = expiry_date
    user.profile.save()

    host = get_current_host(request)

    link = f"{host}/api/reset_password/{token}"
    body = f"Reset your password with this link: {link}"

    send_mail(
        subject = "Your eShop Password Reset Link",
        message = body,
        from_email = "noreply@eshopapi.com",
        recipient_list = [data['email']],
    )

    return Response(
        f"Password Reset Email has been sent to {data['email']}",
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
def reset_password(request, token):
    data = request.data
    user = get_object_or_404(User, profile__reset_password_token=token)

    if user.profile.reset_password_expires.replace(tzinfo=None) < datetime.now():
        return Response(
            'Token expired',
            status=status.HTTP_400_BAD_REQUEST
        )

    if data['password'] != data['confirm_password']:
        return Response(
            'Passwords do not match',
            status=status.HTTP_400_BAD_REQUEST
        )

    user.password = make_password(data['password'])
    user.profile.reset_password_token = ""
    user.profile.reset_password_expires = None
    user.profile.save()
    user.save()

    return Response(
        'Password has been reset',
        status=status.HTTP_200_OK
    )