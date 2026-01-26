from ninja_extra import api_controller, http_get, http_post, NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController
from .schemas import *
from collections import defaultdict
from typing import Dict
from .gpt import get_LLM_completion, get_gemini_title_completion
from core.models import EmailMarketing
from ninja_jwt.authentication import JWTAuth
from django.http import StreamingHttpResponse, HttpResponseServerError
import json
from django.shortcuts import get_object_or_404
from core.middlewares.jwt_verify import JwtVerify
from datetime import datetime, timedelta
from django.db.models import Sum
from django.utils import timezone
from core.prompts.email_prompt import create_email_prompt, create_email_title_prompt

api = NinjaExtraAPI(urls_namespace="EmailMarketing")


email_features = {
    "Standard": {
        "prompt_id": [
            "pp--email-cop-576648",
            "pp--email-cop-82504b",
            "pp--email-cop-12401b",
            "pp--email-cop-5dd2cd",
            "pp--email-cop-5dd2cd",
        ]
    },
    "Casual convo starter": {
        "prompt_id": [
            "pp--email-cop-d1bb7c",
            "pp--email-cop-d1bb7c",
            "pp--email-cop-224906",
            "pp--email-cop-50255b",
            "pp--email-cop-f180f6",
            "pp--email-cop-07117e",
        ]
    },
    "The Goldfish attention span": {
        "prompt_id": [
            "pp--email-cop-1cc201",
            "pp--email-cop-11854f",
            "pp--email-cop-367f46",
        ]
    },
    "Long form (Outreach Copy)": {
        "prompt_id": [
            "pp--email-cop-eeb877",
            "pp--email-cop-6e8204",
            "pp--email-cop-40b2d7",
            "pp--email-cop-c646ca",
            "pp--email-cop-fc577f",
            "pp--email-cop-e81f3c",
            "pp--email-cop-e732a7",
            "pp--email-cop-2deb22",
            "pp--email-cop-bb230d",
        ]
    },
}


@api_controller("", tags=["Email-Marketing"], permissions=[])
class EmailMarketingAPI:

    @http_get("/generate_gpt_response/{id}/{token}", response={200: Dict, 400: Dict})
    def generate_gpt_response(self, id: str, token: str):
        # validate user through token
        jwt_verifier = JwtVerify()
        payload = jwt_verifier.verify_jwt_token(token)
        if payload:
            email_record = get_object_or_404(EmailMarketing, pk=id)
            try:
                prompt = create_email_prompt(
                    email_record.feature_name, email_record)
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
    def create_email_marketing(self, request, data: EmailMarketingCopyInput):
        user_id = request.user
        
        email_marketing = EmailMarketing.objects.create(
            to_pitch=data.to_pitch,
            user=user_id,
            our_offering=data.our_offering,
            prospect_name=data.prospect_name,
            prospect_company=data.prospect_company,
            prospect_niche=data.prospect_niche,
            prospect_contact_about=data.prospect_contact_about,
            cta=data.cta,
            module_credit_cost=data.credits_cost,
            feature_name=data.feature_name,
        )
        return {"id": email_marketing.pk, "post_type": "email_marketing"}
        

    @http_post("/save-response", response={200: Dict, 400: Dict}, auth=JWTAuth())
    def save_generated_response(self, request, data: ChatGPTResponse):
        # save the generated response
        if data.response is not None and data.response != "":
            email_marketing = get_object_or_404(EmailMarketing, pk=data.id)
            # Save the generated response
            email_marketing.response = data.response
            email_marketing_prompt = create_email_title_prompt(
                email_marketing.response)
            email_marketing_title = get_gemini_title_completion(
                email_marketing_prompt)
            email_marketing.title = email_marketing_title
            email_marketing.last_edit = timezone.now()
            email_marketing.save()
            return 200, {"id": email_marketing.pk, "message": "Response has been saved"}
        else:
            print("throwing error")
            return 400, {"message": "Invalid response"}

    @http_get("/view-all", response={200: Dict, 400: Dict}, auth=JWTAuth())
    def get_all_emails(self, request):
        user_id = request.user
        # get_claude_completion(user_id)
        try:
            email_marketing = EmailMarketing.objects.filter(
                user=user_id).order_by("-date_created").values(
                    "date_created",
                    "id",
                    "title",
                    "response",
                    "feature_name",
                    "last_edit",
            )

            grouped_data = defaultdict(list)

            for ad in email_marketing:
                grouped_data[ad["date_created"]].append(
                    {
                        "title": ad["title"],
                        "response": ad["response"],
                        "feature_name": ad["feature_name"],
                        "last_edit": ad["last_edit"],
                        "id": ad["id"],
                    }
                )

            # Serialize the queryset to JSON
            email_marketing_json_converted = [
                {"date_created": date, "email_data": ads}
                for date, ads in grouped_data.items()
            ]

            return 200, {
                "message": "View all your Email Marketings",
                "data": email_marketing_json_converted,
            }
        except Exception as e:
            return 400, {
                "message": str(e),
            }

    @http_get("/view", response={200: Dict, 400: Dict, 403: Dict}, auth=None)
    def get_email_marketing_by_id(self, request, ad_id):
        try:
            email_marketing = get_object_or_404(EmailMarketing, id=ad_id)
            user_authenticated = True
            authorization_header = request.headers.get("Authorization")
            if not authorization_header or not authorization_header.startswith("Bearer "):
                user_authenticated = False
            try:
                token = authorization_header.split(" ")[1]
                payload = JWTAuth().authenticate(request, token)
            except:
                user_authenticated = False
                if (email_marketing.visibility == "Private"):
                    return 403, {
                        "is_authenticated": user_authenticated,
                        "message": "You are not authorized to view this ad",
                    }

            can_edit_on_public = False if not user_authenticated else True if payload.email == email_marketing.user.email else False
            if (email_marketing.visibility == "Public"):
                email_marketing_json_converted = {
                    "title": email_marketing.title,
                    "to_pitch": email_marketing.to_pitch,
                    "our_offering": email_marketing.our_offering,
                    "prospect_name": email_marketing.prospect_name,
                    "prospect_company": email_marketing.prospect_company,
                    "prospect_niche": email_marketing.prospect_niche,
                    "prospect_contact_about": email_marketing.prospect_contact_about,
                    "feature_name": email_marketing.feature_name,
                    "cta": email_marketing.cta,
                    "response": email_marketing.response,
                    "id": email_marketing.id,
                    "date_created": email_marketing.date_created,
                    "visibility": email_marketing.visibility,
                    "can_edit": can_edit_on_public,
                    "is_authenticated": user_authenticated
                }

                return 200, {
                    "message": "View your Facebook Ad",
                    "data": email_marketing_json_converted,
                }
            if (email_marketing.visibility == "Private"):

                if (payload.email == email_marketing.user.email):

                    email_marketing_json_converted = {
                        "title": email_marketing.title,
                        "to_pitch": email_marketing.to_pitch,
                        "our_offering": email_marketing.our_offering,
                        "prospect_name": email_marketing.prospect_name,
                        "prospect_company": email_marketing.prospect_company,
                        "prospect_niche": email_marketing.prospect_niche,
                        "prospect_contact_about": email_marketing.prospect_contact_about,
                        "feature_name": email_marketing.feature_name,
                        "cta": email_marketing.cta,
                        "response": email_marketing.response,
                        "id": email_marketing.id,
                        "date_created": email_marketing.date_created,
                        "visibility": email_marketing.visibility,
                        "can_edit": True,
                        "is_authenticated": user_authenticated

                    }

                    return 200, {
                        "message": "View your Facebook Ad",
                        "data": email_marketing_json_converted,
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
            email_marketing = get_object_or_404(EmailMarketing, id=ad_id)
            if (request.user.email == email_marketing.user.email):
                email_marketing.visibility = data.visibility_status
                email_marketing.save()
                return 200, {"id": email_marketing.pk, "message": "Visibility status changed"}
            else:
                return 403, {
                    "message": "You are not authorized to change visibility"
                }
        except:
            return 400, {
                "message": "Could not change visibility"
            }
        #     email_marketing = get_object_or_404(EmailMarketing, id=ad_id)

        #     # Serialize the queryset to JSON
            # email_marketing_json_converted = {
            #     "to_pitch": email_marketing.to_pitch,
            #     "our_offering": email_marketing.our_offering,
            #     "prospect_name": email_marketing.prospect_name,
            #     "prospect_company": email_marketing.prospect_company,
            #     "prospect_niche": email_marketing.prospect_niche,
            #     "prospect_contact_about": email_marketing.prospect_contact_about,
            #     "feature_name": email_marketing.feature_name,
            #     "cta": email_marketing.cta,
            #     "response": email_marketing.response,
            #     "id": email_marketing.id,
            #     "date_created": email_marketing.date_created,

            # }

        #     return 200, {
        #         "message": "View your Emails",
        #         "data": email_marketing_json_converted,
        #     }
        # except EmailMarketing.DoesNotExist:
        #     return 400, {
        #         "message": "Email does not exist with this Id",
        #     }
        # except Exception as e:
        #     return 400, {
        #         "message": str(e),
        #     }

    @http_get("/cards-count", response={200: Dict, 400: Dict}, auth=JWTAuth())
    def get_all_cards_count(self, request):
        user_id = request.user
        try:
            # Get the total number of ads for the user
            total_ads = EmailMarketing.objects.filter(user=user_id).count()

            # Get the date 7 days ago
            seven_days_ago = datetime.now().date() - timedelta(days=7)

            # Get the total number of ads in the last 7 days
            total_ads_last_7_days = EmailMarketing.objects.filter(
                user=user_id, date_created__gte=seven_days_ago
            ).count()

            total_credits = (
                EmailMarketing.objects.filter(user=user_id).aggregate(
                    Sum("module_credit_cost")
                )["module_credit_cost__sum"]
                or 0
            )
            total_credits_last_7_days = (
                EmailMarketing.objects.filter(
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


api.register_controllers(EmailMarketingAPI, NinjaJWTDefaultController)
