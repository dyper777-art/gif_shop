from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone

from .models import SubscriptionPlan, Product, Subscription, ActionLog


# ----------------------------------------------------
# Product Administration
# ----------------------------------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "subscription_plan", "image_url", "file_url")

    def image_url(self, obj):
        """Return the image URL or a dash if missing."""
        return obj.image.url if obj.image else "-"
    image_url.short_description = "Image URL"

    def file_url(self, obj):
        """Return the file URL or a dash if missing."""
        return obj.file.url if obj.file else "-"
    file_url.short_description = "File URL"


# ----------------------------------------------------
# SubscriptionPlan Administration
# ----------------------------------------------------
@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "daily_limit", "stripe_price_id", "price")
    search_fields = ("name",)


# ----------------------------------------------------
# Subscription Filters
# ----------------------------------------------------
class ActiveSubscriptionFilter(admin.SimpleListFilter):
    """Filter subscriptions based on whether they are active or expired."""
    
    title = "Subscription Status"
    parameter_name = "active_status"

    def lookups(self, request, model_admin):
        return (
            ("active", "Active"),
            ("expired", "Expired"),
        )

    def queryset(self, request, queryset):
        today = timezone.now().date()
        if self.value() == "active":
            return queryset.filter(start_date__lte=today, end_date__gte=today)
        if self.value() == "expired":
            return queryset.exclude(start_date__lte=today, end_date__gte=today)
        return queryset


# ----------------------------------------------------
# Subscription Administration
# ----------------------------------------------------
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "plan",
        "is_active",
        "start_date",
        "end_date",
        "downloads_today",
    )
    list_filter = ("start_date", "end_date", "plan", ActiveSubscriptionFilter)
    readonly_fields = ("downloads_today",)

    def downloads_today(self, obj):
        """Show today's downloads and the plan limit."""
        limit = obj.plan.daily_limit if obj.plan else 0
        return f"{obj.downloads_today()} / {limit}"
    downloads_today.short_description = "Downloads Today / Limit"

    def is_active(self, obj):
        """Boolean display for active subscription."""
        return obj.active()
    is_active.boolean = True
    is_active.short_description = "Active"


# ----------------------------------------------------
# ActionLog Administration (Read-only)
# ----------------------------------------------------
@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "date")
    list_filter = ("date", "user")
    readonly_fields = ("user", "product", "date")
    search_fields = ("user__username", "product__name")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# ----------------------------------------------------
# Inline: Subscription inside User Administration
# ----------------------------------------------------
class SubscriptionInline(admin.StackedInline):
    model = Subscription
    can_delete = False
    max_num = 1
    verbose_name_plural = "Subscription Info"

    fields = ("plan", "downloads_today", "start_date", "end_date")
    readonly_fields = ("downloads_today", "start_date", "end_date")

    def downloads_today(self, obj):
        if not obj or not obj.plan:
            return "0"
        return f"{obj.downloads_today()} / {obj.plan.daily_limit}"
    downloads_today.short_description = "Downloads Today / Limit"


# ----------------------------------------------------
# Inline: Action Logs inside User Administration
# ----------------------------------------------------
class ActionLogInline(admin.TabularInline):
    model = ActionLog
    can_delete = False
    verbose_name_plural = "Action Logs"
    fields = ("product", "date")
    readonly_fields = ("product", "date")
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# ----------------------------------------------------
# Custom User Administration
# ----------------------------------------------------
class CustomUserAdmin(BaseUserAdmin):
    fieldsets = (
        ("User Info", {"fields": ("username", "email", "is_active")}),
    )
    inlines = [SubscriptionInline, ActionLogInline]
    list_display = (
        "username",
        "email",
        "is_active",
        "is_staff",
        "subscription_plan_name",
    )
    list_filter = ("is_active", "is_staff", "subscription__plan")
    search_fields = ("username", "email")

    def subscription_plan_name(self, obj):
        """Show the user's current subscription plan."""
        if hasattr(obj, "subscription") and obj.subscription.plan:
            return obj.subscription.plan.name
        return "No Plan"
    subscription_plan_name.short_description = "Subscription Plan"


# ----------------------------------------------------
# Register Custom User Admin
# ----------------------------------------------------
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
