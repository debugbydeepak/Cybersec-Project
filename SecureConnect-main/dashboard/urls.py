from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.overview, name='overview'),
    path('add-domain/', views.add_domain, name='add_domain'),
    path('verify-domain/<uuid:domain_id>/', views.verify_domain, name='verify_domain'),
    path('api/verify-domain/<uuid:domain_id>/download/', views.download_verification_file, name='download_verification_file'),
    path('api/check-verification/<uuid:domain_id>/', views.check_verification, name='check_verification'),
    path('api/simulate-verification/<uuid:domain_id>/', views.simulate_verification, name='simulate_verification'),
]
