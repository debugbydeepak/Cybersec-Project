from django.urls import path
from . import views

app_name = 'assets'

urlpatterns = [
    path('register/', views.register_domain, name='register'),
    path('verify/<uuid:domain_id>/', views.verify_domain, name='verify'),
]
