from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from datetime import date
import uuid

# ----------------------------
# Custom User Manager
# ----------------------------
class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        if not username:
            raise ValueError("Username must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email=email, username=username, password=password, **extra_fields)


# ----------------------------
# User Model
# ----------------------------
class User(AbstractUser):
    username = models.CharField(max_length=100)  # required
    email = models.CharField(max_length=150, unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]  # must include all required fields for superuser

    objects = CustomUserManager()


class FacebookAd(models.Model):
    PostVisibility = (
        ("Public", "Public"),
        ("Private", "Private"),
        ("Restricted", "Restricted"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service_or_product = models.CharField(max_length=255, blank=True)
    offering_uniqueness = models.TextField(
        blank=True, help_text="What makes our product/service unique"
    )
    ideal_market = models.CharField(max_length=255, blank=True)
    cta = models.CharField(max_length=155, blank=True)
    review_on = models.TextField(
        blank=True, help_text="The review your product received copy pasted"
    )
    reviewer = models.CharField(
        max_length=255, blank=True, help_text="Name of person who left the review"
    )
    reviewed_item = models.TextField(
        blank=True, help_text="Your Service/Product that got the review"
    )
    feature_name = models.CharField(max_length=255)
    response = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True)
    image = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(default=date.today)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module_credit_cost = models.IntegerField(default=0)
    visibility = models.CharField(
        max_length=100, choices=PostVisibility, default="Private")
    last_edit = models.DateTimeField(null=True)


class LinkedinAd(models.Model):
    PostVisibility = (
        ("Public", "Public"),
        ("Private", "Private"),
        ("Restricted", "Restricted"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    feature_name = models.CharField(max_length=255)
    feature_fields = models.JSONField(default=dict)
    response = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(default=date.today)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module_credit_cost = models.IntegerField(default=0)
    title = models.TextField(blank=True)
    visibility = models.CharField(
        max_length=100, choices=PostVisibility, default="Private")
    last_edit = models.DateTimeField(null=True)


class LinkedinComment(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    feature_name = models.CharField(max_length=255, null=True)
    post = models.TextField(blank=True)
    points_to_mention = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    response = models.TextField(blank=True)
    credit_used = models.DecimalField(
        blank=True, null=True, default=0, max_digits=10, decimal_places=1
    )
    module_credit_cost = models.DecimalField(
        default=0, max_digits=10, decimal_places=1)
    date_created = models.DateField(auto_now_add=True)


class ArticleAd(models.Model):
    PostVisibility = (
        ("Public", "Public"),
        ("Private", "Private"),
        ("Restricted", "Restricted"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article_topic = models.CharField(max_length=255)
    seo_keywords = models.CharField(max_length=255, blank=True, null=True)
    research_material = models.TextField(blank=True, null=True)
    article_length = models.CharField(max_length=255)
    feature_name = models.CharField(max_length=255, blank=True, null=True)
    response = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(default=date.today)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module_credit_cost = models.IntegerField(default=0)
    title = models.TextField(blank=True)
    visibility = models.CharField(
        max_length=100, choices=PostVisibility, default="Private")
    last_edit = models.DateTimeField(null=True)


class EmailMarketing(models.Model):
    PostVisibility = (
        ("Public", "Public"),
        ("Private", "Private"),
        ("Restricted", "Restricted"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    feature_name = models.CharField(max_length=255, null=True)
    to_pitch = models.TextField(blank=True)
    our_offering = models.TextField(blank=True)
    prospect_name = models.CharField(max_length=255, blank=True)
    prospect_company = models.CharField(max_length=255, blank=True)
    prospect_niche = models.TextField(blank=True)
    prospect_contact_about = models.TextField(blank=True)
    cta = models.CharField(max_length=255, blank=True)
    your_name = models.CharField(max_length=255, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    response = models.TextField(blank=True)
    module_credit_cost = models.IntegerField(default=0)
    date_created = models.DateTimeField(default=date.today)
    title = models.TextField(blank=True)
    visibility = models.CharField(
        max_length=100, choices=PostVisibility, default="Private")
    last_edit = models.DateTimeField(null=True)


class CustomDoc(models.Model):
    PostVisibility = (
        ("Public", "Public"),
        ("Private", "Private"),
        ("Restricted", "Restricted"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    module_credit_cost = models.IntegerField(default=0)
    date_created = models.DateTimeField(default=date.today)
    title = models.TextField(blank=True)
    visibility = models.CharField(
        max_length=100, choices=PostVisibility, default="Private")
    last_edit = models.DateTimeField(null=True)


class PublicBlog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField()
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField()

