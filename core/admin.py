from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    User,
    FacebookAd,
    LinkedinAd,
    LinkedinComment,
    ArticleAd,
    EmailMarketing,
    CustomDoc,
    PublicBlog,
)

# ----------------------------
# User
# ----------------------------
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "username", "is_staff", "is_active", "is_superuser")
    search_fields = ("email", "username")
    list_filter = ("is_staff", "is_active", "is_superuser")
    ordering = ("email",)

# ----------------------------
# Facebook Ads
# ----------------------------
@admin.register(FacebookAd)
class FacebookAdAdmin(admin.ModelAdmin):
    list_display = ("id", "feature_name", "user", "visibility", "date_created")
    search_fields = ("feature_name", "user__email")
    list_filter = ("visibility", "date_created")
    ordering = ("-date_created",)

# ----------------------------
# Linkedin Ads
# ----------------------------
@admin.register(LinkedinAd)
class LinkedinAdAdmin(admin.ModelAdmin):
    list_display = ("id", "feature_name", "user", "visibility", "date_created")
    search_fields = ("feature_name", "user__email")
    list_filter = ("visibility", "date_created")
    ordering = ("-date_created",)

# ----------------------------
# Linkedin Comments
# ----------------------------
@admin.register(LinkedinComment)
class LinkedinCommentAdmin(admin.ModelAdmin):
    list_display = ("id", "feature_name", "user", "date_created")
    search_fields = ("feature_name", "user__email")
    list_filter = ("date_created",)
    ordering = ("-date_created",)

# ----------------------------
# Article Ads
# ----------------------------
@admin.register(ArticleAd)
class ArticleAdAdmin(admin.ModelAdmin):
    list_display = ("id", "article_topic", "user", "visibility", "date_created")
    search_fields = ("article_topic", "user__email")
    list_filter = ("visibility", "date_created")
    ordering = ("-date_created",)

# --------------------------
# Email Marketing
# --------------------------
@admin.register(EmailMarketing)
class EmailMarketingAdmin(admin.ModelAdmin):
    list_display = ("id", "feature_name", "user", "visibility", "date_created")
    search_fields = ("feature_name", "user__email")
    list_filter = ("visibility", "date_created")
    ordering = ("-date_created",)

# ----------------------------
# Custom Docs
# ----------------------------
@admin.register(CustomDoc)
class CustomDocAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "visibility", "date_created")
    search_fields = ("title", "user__email")
    list_filter = ("visibility", "date_created")
    ordering = ("-date_created",)

# ----------------------------
# Public Blogs
# ----------------------------
@admin.register(PublicBlog)
class PublicBlogAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "date_created")
    search_fields = ("title",)
    list_filter = ("date_created",)
    ordering = ("-date_created",)
