from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from scanner.utils import scrub_pii

def index(request):
    return render(request, 'index.html')

@login_required
def features(request):
    return render(request, 'core/features.html')

def contact_us(request):
    return render(request, 'core/contact.html')

def pricing(request):
    return render(request, 'core/pricing.html')

def docs(request):
    return render(request, 'core/docs.html')

@login_required
def pii_scrubber(request):
    redacted_text = None
    original_text = None
    if request.method == 'POST':
        original_text = request.POST.get('text')
        if original_text:
            redacted_text = scrub_pii(original_text)
            
    return render(request, 'core/pii_scrubber.html', {
        'original_text': original_text,
        'redacted_text': redacted_text
    })
