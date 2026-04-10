from django.db import models
import uuid
from accounts.models import User

class Domain(models.Model):
    VERIFICATION_METHODS = [
        ('DNS', 'DNS TXT Record'),
        ('FILE', 'File Upload'),
        ('EMAIL', 'Email Verification'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='domains')
    domain_url = models.URLField(max_length=255, unique=True, help_text="Target domain (e.g., https://example.com)")
    verification_status = models.BooleanField(default=False)
    verification_method = models.CharField(max_length=10, choices=VERIFICATION_METHODS, default='DNS')
    verification_token = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.verification_token:
            self.verification_token = f"secureway-{uuid.uuid4().hex}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.domain_url} - {'Verified' if self.verification_status else 'Pending'}"
