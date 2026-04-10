from django.db import models
import uuid
from scanner.models import Scan

class Report(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scan = models.OneToOneField(Scan, on_delete=models.CASCADE, related_name='report')
    pdf_file = models.FileField(upload_to='reports/', blank=True, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for Scan {self.scan.id}"
