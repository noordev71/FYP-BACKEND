from ninja import Schema
from typing import Optional


class RegisterInput(Schema):
    password: str
    email: str
    firstname: str
    lastname: str


class LoginInput(Schema):
    email: str
    password: str


class ForgotPasswordInput(Schema):
    email: str


class ResetPasswordInput(Schema):
    userid: str
    token: str
    newpassword: str


class OtpVerifyInput(Schema):
    email: str
    otp_code: str


class LogoutData(Schema):
    refresh_token: str


class FacebookAdCopyInput(Schema):
    service_or_product: Optional[str] = ""
    offering_uniqueness: Optional[str] = ""
    ideal_market: Optional[str] = ""
    cta: Optional[str] = ""
    review_on: Optional[str] = ""
    reviewer: Optional[str] = ""
    reviewed_item: Optional[str] = ""
    feature_name: Optional[str] = ""
    credits_cost: Optional[int] = 0


class LinkedinAdCopyInput(Schema):
    feature_name: str
    feature_fields: dict
    credits_cost: Optional[int] = 0


class ArticleGenerationInput(Schema):
    article_topic: str
    seo_keywords: Optional[str] = ""
    research_material: Optional[str] = ""
    article_length: str
    feature_type: Optional[str] = ""
    credits_cost: Optional[int] = 0


class CustomDocInput(Schema):
    title: str
    content: str
    credits_cost: Optional[int] = 0


class ChatGPTResponse(Schema):
    response: str
    id: str
    credits: float


class CustomDocument(Schema):
    content: str
    id: str
    credits: float


class CustomDocTitle(Schema):
    id: str
    title: str


class ArticleGeneration(Schema):
    token: str
    id: str
    credits: float


class SettingsUpdateInput(Schema):
    email: str
    first_name: str
    last_name: str
    old_password: Optional[str] = ""
    new_password: Optional[str] = ""


class EmailMarketingCopyInput(Schema):
    to_pitch: Optional[str] = ""
    our_offering: Optional[str] = ""
    prospect_name: Optional[str] = ""
    prospect_company: Optional[str] = ""
    prospect_niche: Optional[str] = ""
    prospect_contact_about: Optional[str] = ""
    cta: Optional[str] = ""
    credits_cost: Optional[int] = 0
    feature_name: Optional[str] = ""


class LinkedinCommentSchema(Schema):
    post: Optional[str] = ""
    points_to_mention: Optional[str] = ""
    credits_cost: Optional[float] = 0
    feature_name: Optional[str] = ""


class PaymentMethodSchema(Schema):
    payment_method_id: str


class ChangeVisibilitySchema(Schema):
    visibility_status: str
