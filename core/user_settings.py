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
