from ninja_extra import api_controller, http_get, http_post, NinjaExtraAPI
from collections import defaultdict
from ninja_jwt.controller import NinjaJWTDefaultController
from .schemas import *
from typing import Dict
from .gpt import get_LLM_completion, get_gemini_title_completion
from core.models import FacebookAd
from ninja_jwt.authentication import JWTAuth
from django.http import StreamingHttpResponse, HttpResponseServerError
import json
from django.shortcuts import get_object_or_404
from core.middlewares.jwt_verify import JwtVerify
from datetime import datetime, timedelta
from django.db.models import Sum
from django.utils import timezone
import random
import requests
import os
import json
import base64
import torch
from diffusers import DiffusionPipeline
from PIL import Image
from io import BytesIO
import base64

from core.prompts.facebook_prompts import (
    create_facebook_prompt,
    create_facebook_title_prompt,
)

api = NinjaExtraAPI(urls_namespace="FacebookAdCopy")

# # Load the model
# pipe = DiffusionPipeline.from_pretrained(
#     "stabilityai/stable-diffusion-xl-base-1.0",
#     torch_dtype=torch.float16,
#     use_safetensors=True,
#     variant="fp16",
#     low_cpu_mem_usage=True  # Optimize memory usage
# ).to("cpu")


facebook_features = {
    "Standard": {
        "prompt_id": [
            "pp--ad-copy-decefa",
            "pp--ad-copy-19409c",
            "pp--ad-copy-237024",
            "pp--ad-copy-e6cbef",
            "pp--ad-copy-61338e",
            "pp--ad-copy-73cc2a",
            "pp--ad-copy-21e0e2",
            "pp--ad-copy-f8b430",
            "pp--ad-copy-1b18f4",
            "pp--ad-copy-90633b",
        ]
    },
    "The bullet digestion": {
        "prompt_id": [
            "pp--ad-copy-ba5654",
            "pp--ad-copy-16ddd4",
            "pp--ad-copy-ec449d",
            "pp--ad-copy-1e4894",
            "pp--ad-copy-9b1799",
            "pp--ad-copy-996e1c",
            "pp--ad-copy-e477ad",
        ]
    },
    "The suspense builder": {
        "prompt_id": [
            "pp--ad-copy-4e3d07",
            "pp--ad-copy-dc4d50",
            "pp--ad-copy-fe8a77",
            "pp--ad-copy-7e8572",
            "pp--ad-copy-c3efdd",
        ]
    },
    "The FOMO factory": {
        "prompt_id": [
            "pp--ad-copy-d56d8c",
            "pp--ad-copy-a207c1",
            "pp--ad-copy-570603",
        ]
    },
    "The social proof": {
        "prompt_id": [
            "pp--ad-copy-2b235c",
            "pp--ad-copy-bed667",
        ]
    },
}


@api_controller("", tags=["FacebookAdCopy"], permissions=[])
class FacebookAdCopyAPI:

    def _previous_integration(self, fb_ad_record: FacebookAd):
        for field in fb_ad_record._meta.fields:
            field_name = field.name
            field_value = getattr(fb_ad_record, field_name)
            try:
                facebook_variables = {
                    "Products/Service": fb_ad_record.service_or_product
                    or fb_ad_record.reviewed_item,
                    "What_Makes_Product_Unique": fb_ad_record.offering_uniqueness,
                    "Target_Market": fb_ad_record.ideal_market,
                    "CTA": fb_ad_record.cta,
                    "review": fb_ad_record.review_on,
                    "review_from_name": fb_ad_record.reviewer,
                }
                cleaned_facebook_variables = {
                    key: value
                    for key, value in facebook_variables.items()
                    if value != ""
                }

                random_index = random.randint(
                    0,
                    len(facebook_features[fb_ad_record.feature_name]
                        ["prompt_id"]) - 1,
                )

                # return get_claude_completion(
                #     facebook_features[fb_ad_record.feature_name]["prompt_id"][
                #         random_index
                #     ],
                #     cleaned_facebook_variables,
                # )
            except (ValueError, KeyError) as e:
                return HttpResponseServerError(
                    json.dumps({"error": str(e)}), content_type="application/json"
                )

    @http_get("/generate_gpt_response/{id}/{token}", response={200: Dict, 400: Dict})
    def generate_gpt_response(self, id: str, token: str):
        jwt_verifier = JwtVerify()
        payload = jwt_verifier.verify_jwt_token(token)
        if payload:
            fb_ad_record = get_object_or_404(FacebookAd, pk=id)
            try:
                prompt = create_facebook_prompt(
                    fb_ad_record.feature_name, fb_ad_record)
                # streaming_response = self._previous_integration(fb_ad_record)
                streaming_response = get_LLM_completion(prompt)
                response = StreamingHttpResponse(
                    streaming_response, content_type="text/event-stream"
                )
                response["X-Accel-Buffering"] = "no"
                response["Cache-Control"] = "no-cache"
                print("NOW RES", response)
                return response

            except (ValueError, KeyError) as e:
                print(e)
                return HttpResponseServerError(
                    json.dumps({"error": str(e)}), content_type="application/json"
                )
        else:
            return 400, {"detail": "Unauthorized"}


    def generate_image_from_prompt(self, facebook_ad, prompt, filename=None):
        if not filename:
            filename = f"media/facebook_ads/{facebook_ad.id}.png"
        os.makedirs("media/facebook_ads", exist_ok=True)

        # Generate image
        API_KEY = os.getenv("HUGGINGFACE_API_KEY")
        model_url = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        # Payload to send to the model API
        payload = {
            "inputs": prompt  # Just the prompt, no 'options' needed
        }

        # Send the request to Hugging Face API
        response = requests.post(model_url, headers=headers, json=payload)

        # Check for successful response
        if response.status_code == 200:
            image_data = response.content  # Direct binary content of the image

            # Save the image as a file
            image = Image.open(BytesIO(image_data))
            image.save(filename)
        else:
            print("Error:", response.text)
            return None

        return f"/{filename}"


    @http_post("/create", response={200: Dict, 400: Dict}, auth=JWTAuth())
    
    def create_facebook_ad(self, request, data: FacebookAdCopyInput):
        user_id = request.user

    
        facebook_ad = FacebookAd(
            cta=data.cta,
            user=user_id,
            ideal_market=data.ideal_market,
            offering_uniqueness=data.offering_uniqueness,
            service_or_product=data.service_or_product,
            review_on=data.review_on,
            reviewer=data.reviewer,
            reviewed_item=data.reviewed_item,
            feature_name=data.feature_name,
        )
        prompt = f"{data.service_or_product} for {data.ideal_market}, {data.offering_uniqueness}, CTA: {data.cta}"
        image_url = self.generate_image_from_prompt(facebook_ad, prompt)
        facebook_ad.image = image_url
        print("IMAGE URL", facebook_ad.image)
        facebook_ad.save()
        return {"id": facebook_ad.pk, "post_type": "facebook_ad", "image": "http://127.0.0.1:8000" + image_url}
    

    @http_post("/save-response", response={200: Dict, 400: Dict}, auth=JWTAuth())
    
    def save_generated_response(self, request, data: ChatGPTResponse):
        facebook_ad = get_object_or_404(FacebookAd, pk=data.id)

        if data.response is not None and data.response != "":
            facebook_ad.response = data.response
            facebook_ad_title_prompt = create_facebook_title_prompt( 
                response=facebook_ad.response
            )
            facebook_ad_title = get_gemini_title_completion(
                facebook_ad_title_prompt)
            facebook_ad.title = facebook_ad_title
            facebook_ad.last_edit = timezone.now()
            facebook_ad.save()
            return 200, {"id": facebook_ad.pk, "message": "Response has been saved"}
        else:
            return 400, {"message": "Invalid response"}

    @http_get("/view-all", response={200: Dict, 400: Dict}, auth=JWTAuth())
    
    def get_all_facebook_ad(self, request):
        user_id = request.user
        try:
            facebook_ads = (
                FacebookAd.objects.filter(user=user_id)
                .order_by("-date_created")
                .values(
                    "date_created",
                    "id",
                    "title",
                    "response",
                    "feature_name",
                    "last_edit",
                )
            )

            grouped_data = defaultdict(list)

            for ad in facebook_ads:
                grouped_data[ad["date_created"]].append(
                    {
                        "title": ad["title"],
                        "response": ad["response"],
                        "feature_name": ad["feature_name"],
                        "last_edit": ad["last_edit"],
                        "id": ad["id"],
                    }
                )

            facebook_ads_json_converted = [
                {"date_created": date, "facebook_data": ads}
                for date, ads in grouped_data.items()
            ]

            return 200, {
                "message": "View all your Facebook Ads",
                "data": facebook_ads_json_converted,
            }
        except Exception as e:
            return 400, {
                "message": str(e),
            }

    @http_get("/view", response={200: Dict, 400: Dict, 401: Dict, 403: Dict}, auth=None)
    def get_facebook_ad_by_id(self, request, ad_id):
        try:
            facebook_ad = get_object_or_404(FacebookAd, id=ad_id)
            user_authenticated = True
            authorization_header = request.headers.get("Authorization")
            if not authorization_header or not authorization_header.startswith(
                "Bearer "
            ):
                user_authenticated = False
            try:
                token = authorization_header.split(" ")[1]
                payload = JWTAuth().authenticate(request, token)
            except:
                user_authenticated = False
                if facebook_ad.visibility == "Private":
                    return 403, {
                        "is_authenticated": user_authenticated,
                        "message": "You are not authorized to view this ad",
                    }

            can_edit_on_public = (
                False
                if not user_authenticated
                else True if payload.email == facebook_ad.user.email else False
            )
            if facebook_ad.visibility == "Public":
                facebook_ad_json_converted = {
                    "title": facebook_ad.title,
                    "cta": facebook_ad.cta,
                    "ideal_market": facebook_ad.ideal_market,
                    "offering_uniqueness": facebook_ad.offering_uniqueness,
                    "service_or_product": facebook_ad.service_or_product,
                    "review_on": facebook_ad.review_on,
                    "reviewer": facebook_ad.reviewer,
                    "reviewed_item": facebook_ad.reviewed_item,
                    "response": facebook_ad.response,
                    "feature_name": facebook_ad.feature_name,
                    "date_created": facebook_ad.date_created,
                    "id": facebook_ad.id,
                    "visibility": facebook_ad.visibility,
                    "can_edit": can_edit_on_public,
                    "is_authenticated": user_authenticated,
                }

                return 200, {
                    "message": "View your Facebook Ad",
                    "data": facebook_ad_json_converted,
                }
            if facebook_ad.visibility == "Private":

                if payload.email == facebook_ad.user.email:

                    facebook_ad_json_converted = {
                        "title": facebook_ad.title,
                        "cta": facebook_ad.cta,
                        "ideal_market": facebook_ad.ideal_market,
                        "offering_uniqueness": facebook_ad.offering_uniqueness,
                        "service_or_product": facebook_ad.service_or_product,
                        "review_on": facebook_ad.review_on,
                        "reviewer": facebook_ad.reviewer,
                        "reviewed_item": facebook_ad.reviewed_item,
                        "response": facebook_ad.response,
                        "feature_name": facebook_ad.feature_name,
                        "date_created": facebook_ad.date_created,
                        "id": facebook_ad.id,
                        "visibility": facebook_ad.visibility,
                        "can_edit": True,
                        "is_authenticated": user_authenticated,
                    }

                    return 200, {
                        "message": "View your Facebook Ad",
                        "data": facebook_ad_json_converted,
                    }
                elif user_authenticated:
                    return 403, {
                        "is_authenticated": user_authenticated,
                        "message": "You are not authorized to view this ad",
                    }
                else:
                    return 401, {"message": "You are not authorized to view this ad"}

        except Exception as e:
            return 400, {
                "message": str(e),
            }

    @http_post(
        "/visibility", response={200: Dict, 400: Dict, 403: Dict}, auth=JWTAuth()
    )
    
    def change_visibility(self, request, ad_id, data: ChangeVisibilitySchema):
        try:
            facebook_ad = get_object_or_404(FacebookAd, id=ad_id)
            if request.user.email == facebook_ad.user.email:
                facebook_ad.visibility = data.visibility_status
                facebook_ad.save()
                return 200, {
                    "id": facebook_ad.pk,
                    "message": "Visibility status changed",
                }
            else:
                return 403, {"message": "You are not authorized to change visibility"}
        except:
            return 400, {"message": "Could not change visibility"}

    @http_get("/cards-count", response={200: Dict, 400: Dict}, auth=JWTAuth())
    
    def get_all_cards_count(self, request):
        user_id = request.user
        try:
            total_ads = FacebookAd.objects.filter(user=user_id).count()
            seven_days_ago = datetime.now().date() - timedelta(days=7)
            total_ads_last_7_days = FacebookAd.objects.filter(
                user=user_id, date_created__gte=seven_days_ago
            ).count()

            
            return 200, {
                "message": "View all your Cards data",
                "total_ads": total_ads,
                "total_ads_last_week": total_ads_last_7_days,
            }
        except Exception as e:
            return 400, {
                "message": str(e),
            }


api.register_controllers(FacebookAdCopyAPI, NinjaJWTDefaultController)
