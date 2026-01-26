from ninja_extra import api_controller, http_get, http_post, NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController
from .schemas import *
from collections import defaultdict
from typing import Dict
from .gpt import get_LLM_completion, get_gemini_title_completion
from core.models import LinkedinAd
from ninja_jwt.authentication import JWTAuth
from django.http import StreamingHttpResponse, HttpResponseServerError
import json
from django.shortcuts import get_object_or_404
from core.middlewares.jwt_verify import JwtVerify
from datetime import datetime, timedelta
from django.db.models import Sum
from django.utils import timezone
from core.prompts.linkedin_post_prompt import create_linkedin_post_prompt, create_linkedin_post_title_prompt

api = NinjaExtraAPI(urls_namespace="LinkedinAdCopy")


@api_controller("", tags=["LinkedinAdCopy"], permissions=[])
class LinkedinAdCopyAPI:

    @http_get("/generate_gpt_response/{id}/{token}", response={200: Dict, 400: Dict})
    def generate_gpt_response(self, id: str, token: str):
        jwt_verifier = JwtVerify()
        payload = jwt_verifier.verify_jwt_token(token)
        if payload:
            linkedin_ad_record = get_object_or_404(LinkedinAd, pk=id)

            try:
                # stream_data = get_claude_completion(prompt, generated_field)
                prompt = create_linkedin_post_prompt(
                    linkedin_ad_record.feature_name, linkedin_ad_record
                )
                stream_data = get_LLM_completion(prompt)
                response = StreamingHttpResponse(
                    stream_data, content_type="text/event-stream"
                )
                response["X-Accel-Buffering"] = "no"
                response["Cache-Control"] = "no-cache"
                return response

            except Exception as e:
                return HttpResponseServerError(
                    json.dumps({"error": str(e)}), content_type="application/json"
                )
        else:
            return 400, {"detail": "Unauthorized"}

    @http_post("/create", response={200: Dict, 400: Dict}, auth=JWTAuth())
    def create_linkedin_ad(self, request, data: LinkedinAdCopyInput):
        user_id = request.user
        linkedin_ad = LinkedinAd(
            feature_name=data.feature_name,
            feature_fields=data.feature_fields,
            user=user_id,
            module_credit_cost=data.credits_cost,
        )
        linkedin_ad.save()
        return {"id": linkedin_ad.pk, "post_type": "linkedin_ad"}
        

    @http_post("/save-response", response={200: Dict, 400: Dict}, auth=JWTAuth())
    def save_generated_response(self, request, data: ChatGPTResponse):
        linkedin_ad = get_object_or_404(LinkedinAd, pk=data.id)
        if data.response is not None and data.response != "":
            linkedin_ad.response = data.response
            linkedin_ad_title_prompt = create_linkedin_post_title_prompt(
                response=linkedin_ad.response)
            linkedin_ad_title = get_gemini_title_completion(
                linkedin_ad_title_prompt)
            linkedin_ad.title = linkedin_ad_title
            linkedin_ad.last_edit = timezone.now()
            linkedin_ad.save()
            return 200, {"id": linkedin_ad.pk, "message": "Response has been saved"}
        else:
            print("throwing error")
            return 400, {"message": "Invalid response"}

    @http_get("/view-all", response={200: Dict, 400: Dict}, auth=JWTAuth())
    def get_all_linkedin_ad(self, request):
        user_id = request.user
        try:
            linkedin_ads = LinkedinAd.objects.filter(
                user=user_id).order_by("-date_created").values(
                    "date_created",
                    "id",
                    "title",
                    "response",
                    "feature_name",
                    "last_edit",
            )

            grouped_data = defaultdict(list)

            for ad in linkedin_ads:
                grouped_data[ad["date_created"]].append(
                    {
                        "title": ad["title"],
                        "response": ad["response"],
                        "feature_name": ad["feature_name"],
                        "last_edit": ad["last_edit"],
                        "id": ad["id"],
                    }
                )
            linkedin_ads_json_converted = [
                {"date_created": date, "linkedin_data": ads}
                for date, ads in grouped_data.items()
            ]

            return 200, {
                "message": "View all your Linkedin Ads",
                "data": linkedin_ads_json_converted,
            }
        except Exception as e:
            return 400, {
                "message": str(e),
            }

    @http_get("/view", response={200: Dict, 400: Dict}, auth=None)
    def get_linkedin_ad_by_id(self, request, ad_id):
        try:
            linkedin_ad = get_object_or_404(LinkedinAd, id=ad_id)
            user_authenticated = True
            authorization_header = request.headers.get("Authorization")
            if not authorization_header or not authorization_header.startswith("Bearer "):
                user_authenticated = False
            try:
                token = authorization_header.split(" ")[1]
                payload = JWTAuth().authenticate(request, token)
            except:
                user_authenticated = False
                if (linkedin_ad.visibility == "Private"):
                    return 403, {
                        "is_authenticated": user_authenticated,
                        "message": "You are not authorized to view this ad",
                    }

            can_edit_on_public = False if not user_authenticated else True if payload.email == linkedin_ad.user.email else False
            if (linkedin_ad.visibility == "Public"):
                linkedin_ad_json_converted = {
                    "id": linkedin_ad.id,
                    "title": linkedin_ad.title,
                    "feature_name": linkedin_ad.feature_name,
                    "feature_fields": linkedin_ad.feature_fields,
                    "response": linkedin_ad.response,
                    "date_created": linkedin_ad.date_created,
                    "visibility": linkedin_ad.visibility,
                    "can_edit": can_edit_on_public,
                    "is_authenticated": user_authenticated
                }

                return 200, {
                    "message": "View your Facebook Ad",
                    "data": linkedin_ad_json_converted,
                }
            if (linkedin_ad.visibility == "Private"):

                if (payload.email == linkedin_ad.user.email):

                    linkedin_ad_json_converted = {
                        "id": linkedin_ad.id,
                        "title": linkedin_ad.title,
                        "feature_name": linkedin_ad.feature_name,
                        "feature_fields": linkedin_ad.feature_fields,
                        "response": linkedin_ad.response,
                        "date_created": linkedin_ad.date_created,
                        "visibility": linkedin_ad.visibility,
                        "can_edit": True,
                        "is_authenticated": user_authenticated
                    }

                    return 200, {
                        "message": "View your Facebook Ad",
                        "data": linkedin_ad_json_converted,
                    }
                elif user_authenticated:
                    return 403, {
                        "is_authenticated": user_authenticated,
                        "message": "You are not authorized to view this ad",
                    }
                else:
                    return 401, {
                        "message": "You are not authorized to view this ad"
                    }

        except Exception as e:
            return 400, {
                "message": str(e),
            }

    @http_post("/visibility", response={200: Dict, 400: Dict, 403: Dict}, auth=JWTAuth())
    def change_visibility(self, request, ad_id, data: ChangeVisibilitySchema):
        try:
            linkedin_ad = get_object_or_404(LinkedinAd, id=ad_id)
            if (request.user.email == linkedin_ad.user.email):
                linkedin_ad.visibility = data.visibility_status
                linkedin_ad.save()
                return 200, {"id": linkedin_ad.pk, "message": "Visibility status changed"}
            else:
                return 403, {
                    "message": "You are not authorized to change visibility"
                }
        except:
            return 400, {
                "message": "Could not change visibility"
            }

    @http_get("/cards-count", response={200: Dict, 400: Dict}, auth=JWTAuth())
    def get_all_cards_count(self, request):
        user_id = request.user
        try:
            total_ads = LinkedinAd.objects.filter(user=user_id).count()
            seven_days_ago = datetime.now().date() - timedelta(days=7)

            total_ads_last_7_days = LinkedinAd.objects.filter(
                user=user_id, date_created__gte=seven_days_ago
            ).count()

            total_credits = (
                LinkedinAd.objects.filter(user=user_id).aggregate(
                    Sum("module_credit_cost")
                )["module_credit_cost__sum"]
                or 0
            )
            total_credits_last_7_days = (
                LinkedinAd.objects.filter(
                    user=user_id, date_created__gte=seven_days_ago
                ).aggregate(Sum("module_credit_cost"))["module_credit_cost__sum"]
                or 0
            )

            return 200, {
                "message": "View all your Cards data",
                "total_ads": total_ads,
                "total_ads_last_week": total_ads_last_7_days,
                "total_credits": total_credits,
                "total_credits_last_week": total_credits_last_7_days,
            }
        except Exception as e:
            return 400, {
                "message": str(e),
            }


api.register_controllers(LinkedinAdCopyAPI, NinjaJWTDefaultController)
