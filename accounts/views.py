from django.shortcuts import render

# Create your views here.
def login_view(request):
    return render(request, 'accounts/login.html')

def signup_view(request):
    return render(request, 'accounts/signup.html')

def complete_profile(request):
    return render(request, 'accounts/complete_profile.html')

def logout_view(request):
    next = request.GET.get('next', 'home:index')
    logout(request)
    return redirect(next)

