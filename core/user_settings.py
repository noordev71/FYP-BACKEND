from ninja_extra import api_controller, http_get, http_post, permissions, NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController
from .schemas import *
from typing import Dict
from core.models import User
from ninja_jwt.authentication import JWTAuth
from django.shortcuts import get_object_or_404
from ninja import File
from ninja.files import UploadedFile
from django.core.files.storage import FileSystemStorage
from fyp_original_backend import settings
import uuid
from django.utils import timezone

api = NinjaExtraAPI(urls_namespace="Settings")


@api_controller("", tags=["Settings"], permissions=[])
class SettingsAPI:

    @http_get("/view-user-details", response={200: Dict, 400: Dict}, auth=JWTAuth())
    def view_user_details(self, request):
        user_id = request.user.id
        try:
            user = User.objects.get(id=user_id)
            user_json_converted = {
                "id": user.id,
                "email": user.email,
                # "first_name": user.first_name,
                # "last_name": user.last_name,
            }
            return 200, {"message": "View user details", "data": user_json_converted}
        except User.DoesNotExist:
            return 400, {
                "message": "No user found",
            }

    @http_post("/update-user-details", response={200: Dict, 400: Dict}, auth=JWTAuth())
    def update_user_details(self, request, data: SettingsUpdateInput):
        user_id = request.user.id
        try:
            user = User.objects.get(id=user_id, email=data.email)
        except User.DoesNotExist:
            return 400, {
                "message": "No user found",
            }
        if data.old_password is not None and data.new_password is not None:
            # validate password
            if data.old_password and data.new_password:
                if not user.check_password(data.old_password):
                    return 400, {
                        "message": "Invalid old password",
                    }
                if data.old_password == data.new_password:
                    return 400, {
                        "message": "Your new password cannot be your current password",
                    }
                user.set_password(data.new_password)
        user.save()

        return 200, {
            "message": "User details updated successfully",
            "user_id": user.id,
        }

    @http_get("/user-validated", response={200: Dict, 400: Dict}, auth=JWTAuth())
    def IsUserValidated(self, request):
        user = request.user
        current_date = timezone.now()

        return 200, {
            "valid": True,
            "message": "User is validated",
            "name": user.username,
        }


api.register_controllers(SettingsAPI, NinjaJWTDefaultController)
