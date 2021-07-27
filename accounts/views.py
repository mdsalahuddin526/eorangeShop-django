from django.http.response import HttpResponse
from django.shortcuts import render,redirect
from django.contrib import messages,auth
from django.contrib.auth.models import User
from .forms import RegistrationForm
from .models import Account
from django.contrib.auth.decorators import login_required

# Varification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


'''def signup(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password==password2:
            if User.objects.filter(username=username).exists():
                messages.error(request,'Username already exist')
                return redirect('signup')
            else:
                if User.objects.filter(email=email).exists():
                    messages.error(request,'This email is being used')
                    return redirect('signup')
                else:
                    user = User.objects.create_user(first_name=first_name,last_name=last_name,
                    username=username,email=email,password=password)
                    auth.login(request,user)
                    messages.success(request,'You are registered')
                    return redirect('index')            
        else:
            messages.error(request,'Password not match')
            return redirect('signup')
    else:
        return render (request,'accounts/signup.html')'''

def signup(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split("@")[0] #Here username automatically create from email address before "@" part

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number # In models.py, def create_user() has no 'phone_number' attribute thats why this method
            user.save()

            # USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            # messages.success(request, 'Registration successful')
            return redirect('/accounts/login/?command=verification&email='+email)
    else: 
        form = RegistrationForm()
    context = {
        'form': form,
    }
    return render (request,'accounts/signup.html',context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request,'You are now loged in')
            return redirect ('dashboard')
        else:
            messages.error(request,'Invalid login credential')
            return redirect('login')
    else:
        return render(request,'accounts/login.html')


@login_required(login_url = 'login')
def logout(request):    
    auth.logout(request)
    messages.success(request,'You are now loged out')
    return render (request,'eorange/index.html')


@login_required(login_url = 'login')
def dashboard(request):    
    return render (request,'accounts/dashboard.html')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activate.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('signup')


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
           
            # RESET PASSWORD EMAIL
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exists!')
            return redirect('forgotPassword')
    return render (request,'accounts/forgotPassword.html')

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expaired!')
        return redirect('login')

   

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Password reset successful.')
            return redirect('login')
        else:
            messages.error(request,'Password does not match')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')