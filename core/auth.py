from ninja_extra import NinjaExtraAPI, api_controller, http_post, permissions
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_jwt.tokens import RefreshToken
from django.contrib.auth import authenticate

# from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.tokens import default_token_generator

from django.contrib.auth import get_user_model
from .schemas import *
import random
from django.utils import timezone
from datetime import timedelta
from typing import Dict
from datetime import datetime, timedelta
from ninja_jwt.authentication import JWTAuth



User = get_user_model()


# create api
api = NinjaExtraAPI(urls_namespace="Auth")


@api_controller("", tags=["Authentication"], permissions=[permissions.AllowAny])
class AuthAPI:
    @http_post("/register", response={200: Dict, 400: Dict})
    def register_user(self, data: RegisterInput):
        if User.objects.filter(email=data.email).exists():
            return 400, {"message": "Email already exists"}

        try:
            validate_password(data.password)
        except ValidationError as e:
            return 400, {"message": e.messages}


        user = User.objects.create_user(
            email=data.email,
            password=data.password,
            username=f"{data.firstname} {data.lastname}"
        )

        user.save()

        refresh = RefreshToken.for_user(user)


        return 200, {
            "message": "User registered successfully and email sent",
            "user_id": user.id,
            "user_valid": True,
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }

    @http_post("/login", response={200: Dict, 400: Dict})
    def login_user(self, data: LoginInput):
        try:
            user = authenticate(email=data.email, password=data.password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                # if user.is_free_trial_active:
                #     current_date = timezone.now()
                #     if (
                #         user.total_credits == 0
                #         or current_date > user.subscription_end_date
                #     ):
                #         user.is_free_trial_active = False
                #         user.save()

                return 200, {
                    "message": "Login successfull",
                    "full_name": f"{user.first_name} {user.last_name}",
                    "user_valid": True,
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                }
            else:
                return 400, {"message": "Invalid email or password"}

        except User.DoesNotExist:
            return 400, {"message": "Invalid email or password"}


    @http_post("/logout", response={200: Dict, 400: Dict}, auth=JWTAuth())
    def logout(self, request, data: LogoutData):
        try:
            auth_header = request.headers.get("Authorization")
            if auth_header is None:
                return 400, {"message": "Authorization header missing"}

            token_str = data.refresh_token
            token = RefreshToken(token_str)
            token.blacklist()

            return 200, {"message": "JWT Token Blacklisted"}

        except Exception as e:
            return 400, {
                "message": "Error occured in Blacklisting Token",
                "error": str(e),
            }


api.register_controllers(AuthAPI, NinjaJWTDefaultController)
