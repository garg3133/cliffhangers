# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

# local Django
from .tokens import account_activation_token

User = get_user_model()


# Create your views here.
def login_view(request):
    if request.user.is_authenticated:
        messages.success(request, "You are already logged in.")
        return redirect('home:dashboard')

    next_site = request.GET.get('next', 'home:dashboard')

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        context = {}
        user = authenticate(username=email, password=password)

        if user is not None:
            # For cpanel...
            if not user.is_active:
                context['error'] = 'Account not activated. Please check your inbox.'
                return render(request, 'accounts/login.html', context)
            # ...till here.

            if not user.auth and user.first_name:
                # If User has already completed the profile
                # but is not yet verified by the admin
                context['error'] = 'Your Account is not yet authorised. Kindly contact admin.'
                return render(request, 'accounts/login.html', context)

            login(request, user)
            messages.success(request, "Logged in Successfully!")
            if not user.auth:
                # User not authenticated and doesn't have a profile.
                return redirect('accounts:complete_profile')
            else:
                return redirect(next_site)
        else:
            user = User.objects.filter(email=email)
            if user.exists() and user[0].check_password(password) and not user[0].is_active:
                # Authentication failed because user is not active
                context['error'] = 'Account not activated. Please check your inbox.'
            else:
                context['error'] = 'Invalid credentials'
            return render(request, 'accounts/login.html', context)

    return render(request, 'accounts/login.html')

def signup_view(request):
    if request.user.is_authenticated:
        messages.success(request, "You are already logged in.")
        return redirect('home:dashboard')

    if request.method == 'POST':
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        context = {}
        user = User.objects.filter(email=email)
        if user.exists():
            context['error'] = "Account with entered email already exists"
            return render(request, "accounts/signup.html", context)
        if password1 and password2 and password1 != password2:
            context['error'] = "Passwords don't match"
            return render(request, "accounts/signup.html", context)

        user = User(email=email, is_active=False)
        user.set_password(password1)
        user.save()

        # Send Account Activation Email
        current_site = get_current_site(request)

        from_email = settings.DEFAULT_FROM_EMAIL
        to = [email]
        subject = '[noreply] Acount Activation'
        html_message = render_to_string('accounts/email/account_activation_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        plain_message = strip_tags(html_message)
        send_mail(
            subject, plain_message, from_email, to,
            fail_silently=False, html_message=html_message,
        )
        return redirect('accounts:signup_success')

    return render(request, 'accounts/signup.html')

@login_required
def complete_profile(request):
    """ For completing the Profile after successful signup and activation of account.
        Mandatory before accessing the Dashboard."""
    user = request.user
    next_site = request.GET.get('next', 'accounts:profile_completed')

    # Redirect to Dashboard if Profile is already complete
    if user.first_name:
        if not user.auth:
            # If Profile is complete but user is not authenticated
            # (If user didn't log out after completing profile)
            # (Or somehow user got logged in with auth=False
            # like if user was logged in and admin turned auth=False)
            logout(request)
            return redirect('accounts:login')
        return redirect('home:dashboard')

    if request.method == 'POST':
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.role = request.POST['role']
        user.contact_no = request.POST['contact_no']
        user.save()

        # Notify Admin for New User Sign Up
        current_site = get_current_site(request)

        from_email = settings.DEFAULT_FROM_EMAIL
        to = settings.ADMINS_EMAIL
        subject = '[noreply] New User Signed Up'
        html_message = render_to_string('accounts/email/account_authentication_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':account_activation_token.make_token(user),
        })
        plain_message = strip_tags(html_message)
        send_mail(
            subject, plain_message, from_email, to,
            fail_silently=False, html_message=html_message,
        )

        if not user.auth:
            logout(request)
            return redirect('accounts:profile_completed')
        else:
            # If user is authenticated but needed to complete profile.
            return redirect(next_site)

    return render(request, 'accounts/complete_profile.html', {'roles': User.ROLE})

def logout_view(request):
    next_site = request.GET.get('next', 'home:index')
    logout(request)
    return redirect(next_site)

def account_activation(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64)
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        login(request, user)
        messages.success(request, "Account Activated Successfully!")
        return redirect('accounts:complete_profile')
    else:
        msg = "You have either opened a wrong/expired link or your account has already been activated."
        return render(request, 'accounts/token_expired.html', {'msg': msg, 'act_token': True})

def account_authentication(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64)
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.auth = True
        user.save()

        # Notify User of Account Authenticated
        current_site = get_current_site(request)

        from_email = settings.DEFAULT_FROM_EMAIL
        to = [user.email]
        subject = '[noreply] Account Authenticated'
        html_message = render_to_string('accounts/email/account_authenticated_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':account_activation_token.make_token(user),
        })
        plain_message = strip_tags(html_message)
        send_mail(
            subject, plain_message, from_email, to,
            fail_silently=False, html_message=html_message,
        )

        return redirect('accounts:account_authenticated')
    else:
        msg = "You have either opened a wrong/expired link or some admin has already authenticated this account."
        return render(request, 'accounts/token_expired.html', {'msg': msg})

def signup_success(request):
    return render(request,'accounts/signup_success.html')

def profile_completed(request):
    return render(request,'accounts/profile_completed.html')

def account_authenticated(request):
    return render(request,'accounts/account_authenticated.html')
