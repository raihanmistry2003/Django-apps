from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login as login_process, logout as logout_process
import uuid
import time
import qrcode
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password

def index(request):
    return render(request, 'index.html')

def checkUrl(request, url):
    try:
        data = urls.objects.get(short_url = url)
        data.url_hit_count = data.url_hit_count+1
        data.save()
        return redirect(data.long_url)
    
    except urls.DoesNotExist:
        return redirect('Home')
    
def login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(email = email).first()
        if not user_obj:
            messages.error(request, 'Email is not Found, Try again ..')
            return redirect('Login')

        if not user_obj.is_email_varified:
            messages.warning(request, 'Your email is not verify yet, go to email and verify it first...')
            return redirect('Login')

        valid_user = authenticate(request, email = email, password = password)
        if not valid_user:
            messages.error(request, 'Incorrect Login credential.')
            return redirect('Login')

        login_process(request, valid_user)
        return redirect('Dashboard')

    return render(request, 'Auth/login.html')

def register(request):
    if request.method == "POST":
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            if User.objects.filter(email = email).first():
                messages.error(request, 'Email is already Exists, Try with another one')
                return redirect('Register')
            
            email_token = str(uuid.uuid4())
            user_obj = User(first_name = first_name, last_name = last_name, email = email, email_token = email_token)
            user_obj.set_password(password)
            user_obj.save()
            send_email_after_register(email, email_token)
            messages.success(request, 'Now, go to your email check your inbox or spam box and verify your account.')
            return redirect('Register')

        except Exception as e:
            print(e)
    
    return render(request, 'Auth/register.html')

def send_email_after_register(email, email_token):
    subject = 'Your email id needs to be verified'
    message = f'Hii, Press the link to verify Your Account http://127.0.0.1:8000/verify/{email_token}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

def verify(request, link):
    user_obj = User.objects.filter(email_token = link).first()
    if user_obj:
        if user_obj.is_email_varified:
            messages.warning(request, 'Your email is already verified.')
            return redirect('Login')

        user_obj.is_email_varified = True
        user_obj.save()
        messages.success(request, 'we successfully verified you, now you can login..')
        return redirect('Login')
    else:
        messages.success(request, 'we are unable to verify you, for some issues')
        return redirect('Login')

 
def forgot_email(request):
    if request.method =="POST":
        email = request.POST.get('email')
        if not User.objects.filter(email = email).first():
            messages.error(request, 'Your email is not valid, please enter a valid email')
            return redirect('Forgotemail')
        
        user_obj = User.objects.get(email = email)
        email_token = user_obj.email_token
        send_email_after_forgotpassword(email, email_token)
        messages.success(request, 'Reset password email sent to your email. Please verify')
        return redirect('Forgotemail')
    return render(request, 'Auth/forgotemail.html')

def send_email_after_forgotpassword(email, email_token):
    subject = 'Reset your password'
    message = f'Hii, Press the link to reset your password http://127.0.0.1:8000/resetpassword/{email_token}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

def Resetpassword(request, link):
    if request.method == "POST":
        password = request.POST.get('password')
        
        user_obj = User.objects.filter(email_token = link).first()
        user_obj.set_password(password)
        user_obj.save()
        messages.success(request, 'Password reset successfull. Login with your new password.')
        return redirect('Login')
    return render(request, 'Auth/resetpassword.html')



#------------------------------------------------------------------------------------------
#                               User Dashboard Views
#------------------------------------------------------------------------------------------

@login_required(login_url='Login')
def dashboard(request):
    curr = time.ctime()
    url_obj = urls.objects.all()
    qr_obj = Qrcodes.objects.all()

    context = {
        'current':curr,
        'urls':url_obj,
        'qrcodes': qr_obj,
    }
    return render(request, 'User/dashboard.html', context)

def logout(request):
    logout_process(request)
    messages.success(request, 'Thanks for spending some moment')
    return redirect('Login')

@login_required(login_url='Login')
def Urls(request):
    url_obj = urls.objects.all()
    qr_obj = Qrcodes.objects.all()
    return render(request, 'User/urls.html', {'urls':url_obj, 'qrcodes':qr_obj})

def create_url(request):
    if request.method == "POST":
        email = request.POST.get('email')
        long_url = request.POST.get('long_url')
        short_url = request.POST.get('short_url')
        title = request.POST.get('title')

        if urls.objects.filter(short_url = short_url).first():
            messages.error(request,'Short url already exist, go with a different one.')
            return redirect('Urls')
        
        url_obj = urls(email = email, long_url=long_url, short_url=short_url, title=title)
        url_obj.save()
        messages.success(request,f'{short_url} created successfully.')
        return redirect('Urls')
    return redirect('Urls')

def delete_url(request, surl):
    url_obj = urls.objects.filter(short_url = surl).first()
    if not url_obj:
        messages.warning(request,f'{surl} was not detect in our system')
        return redirect('Urls')
    url_obj.delete()
    messages.success(request,f'{surl} Deleted successfully')
    return redirect('Urls')

def edit_url(request, surl):
    url_obj = urls.objects.get(short_url = surl)
    url = urls.objects.all()
    context = {
        'urls': url,
        'urls_obj': url_obj,
        'title' : 'Update Url',
        'button': 'Update',
    }
    return render(request, 'User/urls.html', context)

def update_url(request, surl):
    if request.method == "POST":
        short_url = request.POST.get('short_url')
        title = request.POST.get('title')
    
    url_obj = urls.objects.get(short_url = surl)

    if urls.objects.filter(short_url = short_url).first():
        messages.error(request,'Short url already exist, go with a different one.')
        return redirect('Urls')
    if not url_obj:
        messages.success(request,f'{surl} not found')
        return redirect('Urls')
    
    url_obj.short_url = short_url
    url_obj.title = title
    url_obj.save()
    messages.success(request,f'{title} update successfully')
    return redirect('Urls')

def user_settings(request):
    if request.method == "POST":
        email = request.POST.get('email')
        profile_pic = request.FILES.get('profile_pic')
        user_obj = User.objects.get(email = email)
        if not user_obj:
            messages.error(request, 'Invalid error')
            return redirect('Settings')
        
        user_obj.profile_pic = profile_pic
        user_obj.save()
        messages.success(request, 'Profile pic updated Successfully')
        return redirect('Settings')
    return render(request, 'User/settings.html')

def qrcodes(request):
    if request.method == "POST":
        email = request.POST.get('email')
        long_url = request.POST.get('long_url')
        title = request.POST.get('title')
      
        qr_obj = Qrcodes(email=email, long_url = long_url, title = title)
        qr_obj.save()
        messages.success(request, f'{title}, successfully created Qr code for this.')
        return redirect('Qrcodes')

    qrcodes = Qrcodes.objects.all()
    return render(request, 'User/qrcode.html', {'qrcode':qrcodes})

def change_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')

        user_obj = User.objects.get(email = email)
        if not user_obj:
            messages.error(request, 'Invalid error')
            return redirect('Settings')
        
        matchpassword = check_password(old_password, user_obj.password)
        if not matchpassword:
            messages.error(request, 'Old password is incorrect, try again with correct password')
            return redirect('Settings')
        else :
            user_obj.set_password(new_password)
            user_obj.save()
            messages.success(request, 'Password change successfully.')
            return redirect('Settings')
    return redirect('Settings')


def create_qr(request, surl):
    url_obj = urls.objects.get(short_url = surl)
    if Qrcodes.objects.filter(long_url = url_obj.long_url).first():
        messages.error(request, 'Qr code already created for this url')
        return redirect('Urls')
    qr_obj = Qrcodes(email = url_obj.email, long_url = url_obj.long_url, title = url_obj.title)
    qr_obj.save()
    messages.success(request, f'Qr code Created successfully for this {url_obj.title}')
    return redirect('Urls')