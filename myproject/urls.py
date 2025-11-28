from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from myapp import views


urlpatterns = [

    # Admin
    path('admin/', admin.site.urls),

    # Public pages
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('activate/<str:code>/', views.activate_view, name='activate'),

    # Profile
    path('profile/', views.profile_view, name='profile'),

    # Downloads
    path('download/<int:product_id>/', views.download_product_api, name='download_product'),

    # Subscription
    path('subscription/', views.subscription_view, name='subscription'),
    path('create_checkout/<int:plan_id>/', views.create_checkout_session, name='create_checkout'),
    path('success/', views.subscription_success, name='checkout_success'),
    path('cancel/', views.subscription_cancel, name='checkout_cancel'),

    # Password Reset
    path("password_reset/", views.password_reset_view, name="password_reset"),
    path("reset/<uidb64>/<token>/", views.password_reset_confirm_view, name="password_reset_confirm"),
    path('reset/done/', views.password_reset_complete_view, name='password_reset_complete'),
]


# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
