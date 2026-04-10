from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from scanner.models import Scan
from .models import Report
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

@login_required
def generate_report(request, scan_id):
    scan = get_object_or_404(Scan, id=scan_id, domain__user=request.user)
    
    # Generate PDF in memory
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    p.setFont("Helvetica-Bold", 24)
    p.drawString(50, 750, "SECUREWAY - AI Vulnerability Report")
    
    p.setFont("Helvetica", 12)
    p.drawString(50, 710, f"Target Domain: {scan.domain.domain_url}")
    p.drawString(50, 690, f"Overall Risk Score: {scan.risk_score}/100")
    p.drawString(50, 670, f"Date: {scan.completed_at}")
    
    y = 630
    for vuln in scan.vulnerabilities.all():
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, f"[{vuln.severity}] {vuln.get_vuln_type_display()} (CVSS: {vuln.cvss_score})")
        y -= 20
        p.setFont("Helvetica", 10)
        p.drawString(50, y, f"Endpoint: {vuln.endpoint}")
        y -= 20
        # AI Explanation
        p.drawString(50, y, f"AI Analysis: {vuln.ai_explanation[:100]}...")
        y -= 40
        if y < 100:
            p.showPage()
            y = 750

    p.showPage()
    p.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="secureway_report_{scan.id}.pdf"'
    
    Report.objects.get_or_create(scan=scan)
    
    return response
