from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'index.html')


def profile_page(request):
    
    return render(request, 'profile.html')

      
