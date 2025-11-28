import os
import django
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

from django.contrib.auth.models import User
from myapp.models import Product, Subscription, SubscriptionPlan

# ------------------------------------
# HELPER FUNCTION
# ------------------------------------
def media_path(path):
    full_path = os.path.join("media", path)
    return full_path if os.path.exists(full_path) else None

# ------------------------------------
# CREATE SUBSCRIPTION PLANS
# ------------------------------------
subscription_plans = [
    {"name": "Free", "daily_limit": 3, "price": 0},
    {"name": "Basic", "daily_limit": 10, "price": 10},
    {"name": "Pro", "daily_limit": 100, "price": 50},
    {"name": "Gold", "daily_limit": 500, "price": 100},
]

plan_objects = {}
for plan_data in subscription_plans:
    plan, created = SubscriptionPlan.objects.get_or_create(
        name=plan_data['name'],
        defaults={
            "daily_limit": plan_data['daily_limit'],
            "price": plan_data['price']
        }
    )
    # Update existing plan if needed
    if not created:
        plan.daily_limit = plan_data['daily_limit']
        plan.price = plan_data['price']
        plan.save()
    plan_objects[plan.name] = plan

# ------------------------------------
# CREATE PRODUCTS
# ------------------------------------
products = [
    {"name": "Free Product 1", "plan": "Free"},
    {"name": "Basic Product 1", "plan": "Basic"},
    {"name": "Pro Product 1", "plan": "Pro"},
    {"name": "Gold Product 1", "plan": "Gold"},
]

for p in products:
    plan = plan_objects[p['plan']]
    product, created = Product.objects.get_or_create(
        name=p['name'],
        subscription_plan=plan
    )

# ------------------------------------
# CREATE USERS AND SUBSCRIPTIONS
# ------------------------------------
users = [
    {"username": "freeuser", "email": "free@example.com", "password": "free123", "plan": "Free"},
    {"username": "basicuser", "email": "basic@example.com", "password": "basic123", "plan": "Basic"},
    {"username": "prouser", "email": "pro@example.com", "password": "pro123", "plan": "Pro"},
    {"username": "golduser", "email": "gold@example.com", "password": "gold123", "plan": "Gold"},
]

for u in users:
    user, created = User.objects.get_or_create(username=u['username'], email=u['email'])
    if created:
        user.set_password(u['password'])
        user.save()

    plan = plan_objects[u['plan']]
    start_date = timezone.now().date()
    end_date = start_date + timedelta(days=365)

    subscription, sub_created = Subscription.objects.get_or_create(
        user=user,
        defaults={
            "plan": plan,
            "start_date": start_date,
            "end_date": end_date
        }
    )
    if not sub_created:
        subscription.plan = plan
        subscription.start_date = start_date
        subscription.end_date = end_date
        subscription.save()

# ------------------------------------
# CREATE SUPERUSER
# ------------------------------------
super_username = "admin"
super_email = "admin@example.com"
super_password = "admin123"

if not User.objects.filter(username=super_username).exists():
    User.objects.create_superuser(super_username, super_email, super_password)
