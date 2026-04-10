from django.db import models
import uuid
from assets.models import Domain

class Scan(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RUNNING', 'Running'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name='scans')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    risk_score = models.IntegerField(default=0, help_text="0-100 score based on vulnerabilities")
    log_output = models.TextField(blank=True, help_text="Terminal-style real-time logs")

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"Scan {self.id} for {self.domain} ({self.status})"

class Vulnerability(models.Model):
    TYPE_CHOICES = [
        ('XSS', 'Cross-Site Scripting (XSS)'),
        ('SQLI', 'SQL Injection (SQLi)'),
        ('BOLA', 'Broken Object Level Authorization (BOLA)'),
        ('SSRF', 'Server-Side Request Forgery (SSRF)'),
        ('OTHER', 'Other Vulnerability'),
    ]

    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scan = models.ForeignKey(Scan, on_delete=models.CASCADE, related_name='vulnerabilities')
    vuln_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    cvss_score = models.FloatField(default=0.0)
    endpoint = models.CharField(max_length=255, blank=True)
    
    # AI and Technical Details
    exploit_path = models.TextField(blank=True)
    proof_of_exploit = models.TextField(blank=True)
    ai_explanation = models.TextField(blank=True)
    ai_fix_suggestion = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_severity_display()} {self.get_vuln_type_display()} on {self.endpoint}"

class PipelineRun(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RUNNING', 'Running'),
        ('SUCCESS', 'Success'),
        ('FAILURE', 'Failure'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name='pipeline_runs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    test_results = models.TextField(blank=True)
    security_results = models.TextField(blank=True)
    autofix_results = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Pipeline {self.id[:8]} - {self.status}"

class AnomalyReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name='anomalies')
    prediction_score = models.FloatField(default=0.0)
    crash_probability = models.FloatField(default=0.0)
    is_anomaly = models.BooleanField(default=False)
    vector_signature = models.TextField(blank=True, help_text="Pinecone similarity signature")
    intel_data = models.JSONField(default=dict, blank=True)
    identified_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Anomaly Report {self.id[:8]} for {self.domain}"
