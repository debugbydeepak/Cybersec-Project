from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('features/', views.features, name='features'),
    path('pricing/', views.pricing, name='pricing'),
    path('contact/', views.contact_us, name='contact'),
    path('docs/', views.docs, name='docs'),
    path('pii-scrubber/', views.pii_scrubber, name='pii_scrubber'),
]
