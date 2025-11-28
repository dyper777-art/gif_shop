import hashlib
import os
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# ---------------------------------------------
# Utility: Generate MD5-based upload filenames
# ---------------------------------------------
def md5_file_upload_path(instance, filename):
    """
    Create a unique filename using an MD5 hash while preserving the original extension.
    A timestamp is added to prevent hash collisions.
    """
    ext = filename.split('.')[-1]  # Extract file extension
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S%f")
    hash_input = f"{filename}{timestamp}".encode("utf-8")
    hashed = hashlib.md5(hash_input).hexdigest()

    # Store the file under 'uploads/images/'
    return os.path.join("uploads/images/", f"{hashed}.{ext}")


# ---------------------------------------------
# Subscription Plan (connected to Stripe Price)
# ---------------------------------------------
class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2)  # Monthly cost
    stripe_price_id = models.CharField(max_length=100, blank=True, null=True)  # Stripe Price ID
    daily_limit = models.IntegerField(default=0)

    def __str__(self):
        return self.name


# ---------------------------------------------
# Product Model
# ---------------------------------------------
class Product(models.Model):
    name = models.CharField(max_length=100)
    subscription_plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.CASCADE,
        default=1  # Assumes a subscription plan with ID=1 (e.g., "Free")
    )
    image = models.ImageField(
        upload_to=md5_file_upload_path,
        blank=True,
        null=True,
        default="default.jpg"
    )
    file = models.FileField(upload_to=md5_file_upload_path, blank=True, null=True)

    def __str__(self):
        return self.name


# ---------------------------------------------
# User Subscription
# ---------------------------------------------
class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to=md5_file_upload_path, blank=True, null=True)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()

    def active(self):
        """Return True if today's date is within the subscription period."""
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date

    def downloads_today(self):
        """Total number of downloads performed by the user today."""
        today = timezone.now().date()
        return ActionLog.objects.filter(user=self.user, date=today).count()

    def paid_this_month(self):
        """Return True if the subscription began this month."""
        today = timezone.now().date()
        return (
            self.start_date.year == today.year
            and self.start_date.month == today.month
        )

    def __str__(self):
        plan_name = self.plan.name if self.plan else "No Plan"
        return f"{self.user.username} - {plan_name}"


# ---------------------------------------------
# Download / Action Log
# ---------------------------------------------
class ActionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Action Log"
        verbose_name_plural = "Action Logs"

    def __str__(self):
        return f"{self.user.username} downloaded {self.product.name} on {self.date}"
