from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

def register_user(request):
     if request.method == 'POST':
        username = request.POST['username']   
        password = request.POST['password']   
        email = request.POST['email']       

         
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('register')  
        
        user = User.objects.create_user(username=username, password=password, email=email)
        user.save()

        group, created = Group.objects.get_or_create(name='Library Members')

        user.groups.add(group)

        user.save()


        messages.success(request, 'Registration successful! You can now log in.')
        return redirect('login')
    
        return render(request, 'registration/register.html')