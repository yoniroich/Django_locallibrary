from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

def register(request):
    """Register a new user using Django's built-in UserCreationForm."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # אחרי רישום מוצלח, עובר לעמוד ההתחברות
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
