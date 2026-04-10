from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User, AuditLog

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            AuditLog.objects.create(user=user, action='Login successful', ip_address=request.META.get('REMOTE_ADDR'))
            # Safe redirect to fallback since dashboard isn't linked yet, but will be
            return redirect('/dashboard/') 
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        class CustomUserCreationForm(UserCreationForm):
            class Meta:
                model = User
                fields = ('username', 'email')
                
        form = CustomUserCreationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            # Explicitly specify backend to avoid multiple backends issue
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            AuditLog.objects.create(user=user, action='Registration successful', ip_address=request.META.get('REMOTE_ADDR'))
            return redirect('/dashboard/')
    else:
        class CustomUserCreationForm(UserCreationForm):
            class Meta:
                model = User
                fields = ('username', 'email')
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def logout_view(request):
    if request.user.is_authenticated:
        AuditLog.objects.create(user=request.user, action='Logout', ip_address=request.META.get('REMOTE_ADDR'))
    logout(request)
    return redirect('core:index')
