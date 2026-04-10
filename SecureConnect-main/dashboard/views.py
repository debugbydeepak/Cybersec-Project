from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
import requests
from scanner.models import Scan, Vulnerability
from assets.models import Domain
from scanner.plots import (
    get_threat_intensity_plot, get_vuln_distribution_plot, 
    get_response_latency_plot, get_attack_surface_radar_plot
)

@login_required
def overview(request):
    domains = Domain.objects.filter(user=request.user)
    scans = Scan.objects.filter(domain__in=domains).order_by('-started_at')[:5]
    total_scans = Scan.objects.filter(domain__in=domains).count()
    total_vulns = Vulnerability.objects.filter(scan__domain__in=domains).count()
    
    # Calculate average risk score
    all_scans = Scan.objects.filter(domain__in=domains)
    avg_risk = sum([s.risk_score for s in all_scans]) / all_scans.count() if all_scans.exists() else 0

    # Calculate REAL vulnerability statistics for the user
    vuln_counts = {
        'BOLA': Vulnerability.objects.filter(scan__domain__in=domains, vuln_type='BOLA').count(),
        'XSS': Vulnerability.objects.filter(scan__domain__in=domains, vuln_type='XSS').count(),
        'SQLI': Vulnerability.objects.filter(scan__domain__in=domains, vuln_type='SQLI').count(),
        'SSRF': Vulnerability.objects.filter(scan__domain__in=domains, vuln_type='SSRF').count(),
        'OTHER': Vulnerability.objects.filter(scan__domain__in=domains, vuln_type='OTHER').count(),
    }

    context = {
        'total_scans': total_scans,
        'total_vulns': total_vulns,
        'avg_risk': round(avg_risk),
        'recent_scans': scans,
        'domains': domains,
        'threat_plot': get_threat_intensity_plot(),
        'vuln_plot': get_vuln_distribution_plot(counts=vuln_counts),
        'latency_plot': get_response_latency_plot(),
        'radar_plot': get_attack_surface_radar_plot(),
    }
    return render(request, 'dashboard/overview.html', context)

@login_required
def add_domain(request):
    if request.method == 'POST':
        domain_url = request.POST.get('domain_url')
        if domain_url:
            domain = Domain.objects.create(user=request.user, domain_url=domain_url, verification_method='FILE')
            return redirect('dashboard:verify_domain', domain_id=domain.id)
    return render(request, 'dashboard/add_domain.html')

@login_required
def verify_domain(request, domain_id):
    domain = get_object_or_404(Domain, id=domain_id, user=request.user)
    return render(request, 'dashboard/verify_domain.html', {'domain': domain})

@login_required
def download_verification_file(request, domain_id):
    domain = get_object_or_404(Domain, id=domain_id, user=request.user)
    content = f"secureway-verification={domain.verification_token}"
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{domain.verification_token}.txt"'
    return response

@login_required
@require_POST
def check_verification(request, domain_id):
    domain = get_object_or_404(Domain, id=domain_id, user=request.user)
    
    if domain.verification_status:
        return JsonResponse({'status': 'verified', 'message': 'Domain is already verified.'})
        
    url = f"{domain.domain_url.rstrip('/')}/{domain.verification_token}.txt"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200 and f"secureway-verification={domain.verification_token}" in response.text:
            domain.verification_status = True
            domain.save()
            return JsonResponse({'status': 'verified', 'message': 'Verification successful!'})
        else:
            return JsonResponse({'status': 'failed', 'message': 'File content mismatch or file not found.'})
    except requests.exceptions.RequestException as e:
        return JsonResponse({'status': 'error', 'message': f'Failed to fetch the file: {str(e)}'})

@login_required
@require_POST
def simulate_verification(request, domain_id):
    """Bypasses real verification for showcase purposes."""
    domain = get_object_or_404(Domain, id=domain_id, user=request.user)
    domain.verification_status = True
    domain.save()
    return JsonResponse({'status': 'verified', 'message': 'Simulated verification completed for showcase.'})
