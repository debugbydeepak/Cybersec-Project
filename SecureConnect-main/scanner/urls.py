from django.urls import path
from . import views

app_name = 'scanner'

urlpatterns = [
    path('new/', views.new_scan, name='new_scan'),
    path('port-scan/', views.port_scan, name='port_scan'),
    path('analyze-bola/', views.analyze_bola, name='analyze_bola'),
    path('pipeline/', views.pipeline, name='pipeline'),
    path('threat-intel/', views.threat_intel, name='threat_intel'),
    path('shadow-map/', views.shadow_map, name='shadow_map'),
    path('anomalies/', views.anomalies, name='anomalies'),
    path('history/', views.scan_history, name='scan_history'),
    path('scan-detail/<uuid:scan_id>/', views.scan_detail, name='scan_detail'),
    path('download-report/<uuid:scan_id>/', views.download_report, name='download_report'),
    path('download-all-vulnerabilities/', views.download_all_vulnerabilities, name='download_all_vulnerabilities'),
    path('oast-mesh/', views.oast_mesh, name='oast_mesh'),
    path('kernel-status/', views.kernel_status, name='kernel_status'),
]
