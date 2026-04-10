from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Domain

@login_required
def register_domain(request):
    if request.method == 'POST':
        domain_url = request.POST.get('domain_url')
        method = request.POST.get('verification_method', 'DNS')
        
        if domain_url:
            domain, created = Domain.objects.get_or_create(
                user=request.user, 
                domain_url=domain_url,
                defaults={'verification_method': method}
            )
            return redirect('assets:verify', domain_id=domain.id)
            
    return render(request, 'assets/register.html')

@login_required
def verify_domain(request, domain_id):
    domain = get_object_or_404(Domain, id=domain_id, user=request.user)
    
    if request.method == 'POST':
        # Simulate verification MVP
        domain.verification_status = True
        domain.save()
        return redirect('dashboard:overview')
        
    return render(request, 'assets/verify.html', {'domain': domain})
