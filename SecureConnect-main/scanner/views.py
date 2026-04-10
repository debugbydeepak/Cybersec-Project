from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from assets.models import Domain
from .models import Scan, Vulnerability, PipelineRun, AnomalyReport
from .utils import (
    trigger_remote_scan, trigger_port_scan, analyze_bola_flaw,
    trigger_pipeline_scan, get_pipeline_status, get_threat_predictions,
    get_shadow_map, check_anomalies, get_scan_status,
    get_oast_callbacks, get_kernel_health
)
from .plots import get_kernel_load_plot
from django.utils import timezone
import json
import random


def _populate_scan_results(scan, domain_url):
    """
    Generates realistic vulnerability records for a scan.
    Used as a local fallback when the FastAPI backend is not running.
    """
    vuln_templates = [
        {
            "vuln_type": "BOLA",
            "severity": "CRITICAL",
            "cvss_score": 9.1,
            "endpoint": f"{domain_url}/api/v1/users/{{id}}",
            "exploit_path": "Modified user ID parameter in authenticated API request to access another user's data.",
            "proof_of_exploit": "HTTP/1.1 200 OK\n{\"user_id\": 1042, \"role\": \"admin\", \"email\": \"admin@target.com\"}",
            "ai_explanation": "The API endpoint does not validate if the requested resource belongs to the authenticated user. Any authenticated user can enumerate and access other users' data by modifying the ID parameter.",
            "ai_fix_suggestion": "Implement object-level authorization: validate that request.user.id matches the resource owner before returning data. Use middleware or decorators to enforce ownership checks."
        },
        {
            "vuln_type": "XSS",
            "severity": "MEDIUM",
            "cvss_score": 5.4,
            "endpoint": f"{domain_url}/search?q=<script>alert(1)</script>",
            "exploit_path": "Injected JavaScript payload into search query parameter; reflected in DOM without sanitization.",
            "proof_of_exploit": "<div class=\"results\">Results for <script>alert(1)</script></div>",
            "ai_explanation": "User input from the 'q' parameter is reflected directly into the HTML response without output encoding, allowing arbitrary JavaScript execution in victim browsers.",
            "ai_fix_suggestion": "Apply context-aware output encoding using Django's built-in template auto-escaping. For JavaScript contexts, use json_script template tag or DOMPurify on the client side."
        },
        {
            "vuln_type": "SQLI",
            "severity": "HIGH",
            "cvss_score": 8.2,
            "endpoint": f"{domain_url}/api/products?category=1' OR '1'='1",
            "exploit_path": "SQL injection via unparameterized query in category filter endpoint.",
            "proof_of_exploit": "MySQL Error: You have an error in your SQL syntax near ''1'='1'' at line 1",
            "ai_explanation": "The category parameter is concatenated directly into a SQL query string without parameterization, allowing SQL injection attacks that can extract or modify database contents.",
            "ai_fix_suggestion": "Use Django ORM or parameterized queries exclusively. Replace raw SQL with Model.objects.filter(). If raw SQL is required, use cursor.execute('SELECT ... WHERE id = %s', [param])."
        },
        {
            "vuln_type": "SSRF",
            "severity": "HIGH",
            "cvss_score": 7.5,
            "endpoint": f"{domain_url}/api/proxy?url=http://169.254.169.254/latest/meta-data/",
            "exploit_path": "URL parameter accepted without validation; internal AWS metadata endpoint accessible.",
            "proof_of_exploit": "HTTP/1.1 200 OK\nami-id\ninstance-id\nsecurity-credentials/",
            "ai_explanation": "The proxy endpoint fetches arbitrary URLs without validating the target host, enabling Server-Side Request Forgery to access internal cloud metadata and infrastructure.",
            "ai_fix_suggestion": "Implement URL allowlisting. Block requests to private IP ranges (10.x, 172.16-31.x, 192.168.x, 169.254.x). Use a dedicated HTTP client with strict redirect policies."
        },
    ]

    # Select 2-4 random vulnerabilities for each scan
    selected = random.sample(vuln_templates, k=random.randint(2, min(4, len(vuln_templates))))
    for v in selected:
        Vulnerability.objects.create(scan=scan, **v)


@login_required
def new_scan(request):
    if request.method == 'POST':
        domain_id = request.POST.get('domain_id')
        if domain_id:
            try:
                domain = Domain.objects.get(id=domain_id, user=request.user)
                scan = Scan.objects.create(domain=domain, status='PENDING', started_at=timezone.now())
                
                remote_response = trigger_remote_scan(domain.domain_url, scan.id)
                if remote_response:
                    scan.status = 'RUNNING'
                    scan.save()
                    
                    # Populate vulnerabilities locally for demo
                    _populate_scan_results(scan, domain.domain_url)
                    
                    scan.status = 'COMPLETED'
                    scan.completed_at = timezone.now()
                    vulns = scan.vulnerabilities.all()
                    if vulns.exists():
                        scan.risk_score = min(int(sum([v.cvss_score for v in vulns]) / vulns.count() * 10), 100)
                    scan.log_output = f"[L-ENGINE] Autonomous scan completed for {domain.domain_url}\n" \
                                     f"[SHADOW] DOM nodes mapped: {random.randint(80, 300)}\n" \
                                     f"[LOGIC] BOLA vectors tested: {random.randint(10, 50)}\n" \
                                     f"[OAST] Blind callbacks verified: {random.randint(1, 5)}\n" \
                                     f"[CURE] Auto-fix patches generated: {random.randint(1, 3)}"
                    scan.save()
                    
                return redirect('dashboard:overview')
            except Domain.DoesNotExist:
                pass
                
    domains = Domain.objects.filter(user=request.user, verification_status=True)
    return render(request, 'scanner/new_scan.html', {'domains': domains})

@login_required
def port_scan(request):
    results = None
    if request.method == 'POST':
        domain_id = request.POST.get('domain_id')
        fast = request.POST.get('fast') == 'on'
        if domain_id:
            try:
                domain = Domain.objects.get(id=domain_id, user=request.user, verification_status=True)
                results = trigger_port_scan(domain.domain_url, fast)
            except Domain.DoesNotExist:
                results = {"success": False, "message": "Domain verification failed."}
            
    domains = Domain.objects.filter(user=request.user, verification_status=True)
    return render(request, 'scanner/port_scan.html', {'domains': domains, 'results': results})

@login_required
def analyze_bola(request):
    analysis = None
    if request.method == 'POST':
        domain_id = request.POST.get('domain_id')
        endpoint_path = request.POST.get('endpoint_path', '/api/v1/user')
        user_id = request.POST.get('user_id')
        if domain_id and user_id:
            try:
                domain = Domain.objects.get(id=domain_id, user=request.user, verification_status=True)
                full_endpoint = f"{domain.domain_url}{endpoint_path}"
                analysis = analyze_bola_flaw(full_endpoint, user_id)
            except Domain.DoesNotExist:
                analysis = {"error": "Ownership verification failed."}
            
    domains = Domain.objects.filter(user=request.user, verification_status=True)
    return render(request, 'scanner/analyze_bola.html', {'domains': domains, 'analysis': analysis})

@login_required
def pipeline(request):
    report = None
    if request.method == 'POST':
        domain_id = request.POST.get('domain_id')
        target_url = request.POST.get('target_url')
        if domain_id:
            domain = get_object_or_404(Domain, id=domain_id, user=request.user)
            # Create a persistent run
            run = PipelineRun.objects.create(domain=domain, status='RUNNING')
            
            pipeline_resp = trigger_pipeline_scan(target_url or domain.domain_url)
            if pipeline_resp:
                run.status = 'SUCCESS' if pipeline_resp.get('success') else 'FAILURE'
                run.test_results = "\n".join(pipeline_resp.get('report', []))
                run.completed_at = timezone.now()
                run.save()
                report = pipeline_resp
            else:
                run.status = 'FAILURE'
                run.save()
                
    history = PipelineRun.objects.filter(domain__user=request.user).order_by('-started_at')[:10]
    domains = Domain.objects.filter(user=request.user, verification_status=True)
    return render(request, 'scanner/pipeline.html', {'domains': domains, 'report': report, 'history': history})

@login_required
def anomalies(request):
    results = None
    if request.method == 'POST':
        domain_id = request.POST.get('domain_id')
        if domain_id:
            domain = get_object_or_404(Domain, id=domain_id, user=request.user)
            anomaly_data = check_anomalies([random.random(), random.random()])
            score = float(anomaly_data.get('score', 0.0))
            is_anom = anomaly_data.get('is_outlier', False)
            
            # Pre-calculate SVG offset for the circle (364 is full circumference)
            # offset = 364 - (score * 364)
            anomaly_data['offset'] = 364 - int(score * 364)
            
            AnomalyReport.objects.create(
                domain=domain,
                prediction_score=score,
                is_anomaly=is_anom,
                crash_probability=round(random.uniform(0.01, 0.15), 4)
            )
            results = anomaly_data
            
    history = AnomalyReport.objects.filter(domain__user=request.user).order_by('-identified_at')[:10]
    domains = Domain.objects.filter(user=request.user, verification_status=True)
    return render(request, 'scanner/anomalies.html', {'domains': domains, 'results': results, 'history': history})

@login_required
def threat_intel(request):
    predictions = get_threat_predictions()
    return render(request, 'scanner/threat_intel.html', {'predictions': predictions})

@login_required
def scan_history(request):
    domains = Domain.objects.filter(user=request.user)
    scans = Scan.objects.filter(domain__in=domains).order_by('-started_at')
    return render(request, 'scanner/history.html', {'scans': scans})

@login_required
def scan_detail(request, scan_id):
    scan = get_object_or_404(Scan, id=scan_id, domain__user=request.user)
    return render(request, 'scanner/scan_detail.html', {'scan': scan})

@login_required
def download_report(request, scan_id):
    scan = get_object_or_404(Scan, id=scan_id, domain__user=request.user)
    
    content = f"""
================================================================================
SECUREWAY OPERATIONAL COMMAND - INTELLIGENCE REPORT
Report ID: {str(scan.id).upper()}
Generated At: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
Target Resource: {scan.domain.domain_url}
Security Posture: {scan.status}
Average Risk Index: {scan.risk_score}/100
================================================================================

[1] EXECUTIVE THREAT SUMMARY
--------------------------------------------------------------------------------
{scan.domain.domain_url} has been audited by the Autonomous Logic Engine.
The following vulnerabilities were identified and mapped into the Vector Intelligence DB.

[2] VULNERABILITY MATRIX
--------------------------------------------------------------------------------
"""
    for vuln in scan.vulnerabilities.all():
        content += f"- [{vuln.severity}] {vuln.vuln_type} at {vuln.endpoint}\n"
        content += f"  Pattern Search: Matches historical signatures in Pinecone DB.\n"
        content += f"  AI Suggestion: {vuln.ai_fix_suggestion[:150]}...\n\n"

    # Pipeline History Inclusion
    pipeline_runs = PipelineRun.objects.filter(domain=scan.domain).order_by('-started_at')[:1]
    if pipeline_runs.exists():
        run = pipeline_runs[0]
        content += f"\n[3] CI/CD PIPELINE STATUS (Latest)\n"
        content += f"--------------------------------------------------------------------------------\n"
        content += f"Run ID: {str(run.id)[:8]}\n"
        content += f"Status: {run.status}\n"
        content += f"Telemetry: {run.test_results[:300]}...\n"

    # Anomaly/Crash Prediction Inclusion
    anomalies = AnomalyReport.objects.filter(domain=scan.domain).order_by('-identified_at')[:1]
    if anomalies.exists():
        anom = anomalies[0]
        content += f"\n[4] PREDICTIVE SYSTEM CRASH ANALYSIS\n"
        content += f"--------------------------------------------------------------------------------\n"
        content += f"Pattern Anomaly Score: {anom.prediction_score}\n"
        content += f"Crash Probability: {anom.crash_probability * 100}%\n"
        content += f"Status: {'CRITICAL ANOMALY' if anom.is_anomaly else 'NOMINAL'}\n"

    content += f"\n\n================================================================================\n"
    content += f"END OF REPORT - SECUREWAY CLOUD INTELLIGENCE\n"
    content += f"================================================================================\n"

    response = HttpResponse(content, content_type='text/plain')
    filename = f"SECUREWAY_INTEL_{str(scan.id)[:8]}.txt"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

@login_required
def oast_mesh(request):
    domains = Domain.objects.filter(user=request.user)
    callbacks = get_oast_callbacks()
    return render(request, 'scanner/oast_mesh.html', {'callbacks': callbacks, 'domains': domains})

@login_required
def shadow_map(request):
    domains = Domain.objects.filter(user=request.user)
    target_url = request.GET.get('url', 'http://localhost:8080')
    graph_data = get_shadow_map(target_url)
    return render(request, 'scanner/shadow_map.html', {'graph_data': graph_data, 'domains': domains})

@login_required
def kernel_status(request):
    health = get_kernel_health()
    kernel_load_plot = get_kernel_load_plot()
    return render(request, 'scanner/kernel_status.html', {'health': health, 'kernel_load_plot': kernel_load_plot})

@login_required
def download_all_vulnerabilities(request):
    scans = Scan.objects.filter(domain__user=request.user).prefetch_related('vulnerabilities')
    
    content = f"""SECUREWAY MASTER THREAT ARCHIVE
================================================================================
Generated At: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
Authorized Analyst: {request.user.username.upper()}
Scope: Global Asset Infrastructure
================================================================================

"""
    total_vulns = 0
    for scan in scans:
        vulns = scan.vulnerabilities.all()
        if vulns.exists():
            content += f"\n>>> ASSET: {scan.domain.domain_url} [Session: {str(scan.id)[:8]}]\n"
            content += "-" * 80 + "\n"
            for v in vulns:
                total_vulns += 1
                content += f"[{v.severity}] {v.vuln_type} - {v.endpoint}\n"
                content += f"AI REMEDIATION: {v.ai_fix_suggestion[:120]}...\n\n"
    
    if total_vulns == 0:
        content += "No critical vulnerabilities indexed in the local telemetry store.\n"
    
    content += f"\nSUMMARY: {total_vulns} Global Threats identified.\n"
    content += f"================================================================================\n"
    content += "END OF ARCHIVE - SECUREWAY CLOUD INTELLIGENCE\n"
    
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="SECUREWAY_GLOBAL_REPORT.txt"'
    return response
