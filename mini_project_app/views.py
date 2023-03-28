from django.shortcuts import render, redirect
from passlib.hash import sha512_crypt as sha512
from .models import User, Talker, Messages
import random
import string
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
import os
from django.core.mail import send_mail
from dotenv import load_dotenv
load_dotenv()

otp:str
otp_forgot_password:str

# Index page logs user in if private key exists else produces login page.
def index(request):
    # Checks if private key element is present in request.session
    if 'private_mini_project_key' not in request.session:
        return redirect('login')
    else:
        # If present now checks if private key is present in database
        if User.objects.filter(private_key=request.session['private_mini_project_key']).exists():
            # If yes User is logged in
            return redirect('home')
        else:
            return redirect('login')


def home(request):
    # Reruns all checks done in index function in case someone directly enters home page url will return to login if not
    if 'private_mini_project_key' not in request.session:
        return redirect('login')
    else:
        if User.objects.filter(private_key=request.session['private_mini_project_key']).exists():
            user=User.objects.get(private_key=request.session['private_mini_project_key'])
            talkers=Talker.objects.filter(sender_email=user.email)
            return render(request,'home.html',{'user':user,'username':str(user.name).capitalize(),'sender_email':user.email,'talkers':talkers})
        else:
            return redirect('login')


# Chat functions

def newtalker(request):
    recepient=request.POST['recepient']
    if User.objects.filter(private_key=request.session['private_mini_project_key']).exists():
        user=User.objects.get(private_key=request.session['private_mini_project_key'])
        user2=User.objects.get(email=recepient)
        if not Talker.objects.filter(receiver_email=recepient, sender_email=user.email).exists():
            roomcode=''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(30))
            Talker.objects.create(roomcode=roomcode,sender_email=user.email,receiver_email=recepient,sender_name=user.name,receiver_name=user2.name)
            Talker.objects.create(roomcode=roomcode,sender_email=user2.email,receiver_email=user.email,sender_name=user2.name,receiver_name=user.name)
            return redirect('home')
        else:
            messages.info(request,"User Already Exists in Your Chats !")
            return redirect('home')
    else:
        messages.info(request,"No such user exists")
        return redirect('home')

def send_message(request):
    sender=request.POST['sender']
    receiver=request.POST['receiver']
    message=request.POST['message']
    roomcode=request.POST['roomcode']
    print(sender+" "+receiver+" "+message+" "+roomcode)
    Talker.objects.filter(sender_email=receiver,roomcode=roomcode).update(new_message=True,last_message=message)
    Messages.objects.create(roomcode=roomcode,sender_email=sender,receiver_email=receiver,message=message,sender_name=User.objects.get(email=sender).name,receiver_name=User.objects.get(email=receiver).name,encrypted_img_path='nill')
    return JsonResponse({'message':message})

def set_all_messages(request):
    roomcode=request.POST['roomcode']
    messages=Messages.objects.filter(roomcode=roomcode)
    temp=list(messages.values())
    talker=Talker.objects.filter(roomcode=roomcode)
    for x in talker:
        x.new_message=False
        x.save()
    return JsonResponse({'messages':temp})

def check_for_new_messages(request):
    roomcode=request.POST['room_code']
    sender=request.POST['sender']
    talker=Talker.objects.filter(roomcode=roomcode,sender_email=sender)
    for talker in talker:
        if talker.new_message:
            print(talker.last_message)
            talker.new_message=False
            talker.save()
            return JsonResponse({'new_message':talker.last_message})
            
        else:
            return JsonResponse({'new_message':'na'})
            

def encryptimage(request):
    img=request.FILES['image']
    key=request.POST['key']
    sm=request.POST['sender_email']
    rm=request.POST['receiver_email']
    roomcode=request.POST['roomcode']
    name=img.name
    name_change=''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(30))
    name=name_change+"_"+name
    file_name = FileSystemStorage().save("mini_project_app/static/encrypted_image/"+name, img)
    fin = open("mini_project_app/static/encrypted_image/"+name, 'rb')
    image = fin.read()
    fin.close()
    image = bytearray(image)
    ascii_values = [ord(character) for character in key]
    max=0
    for x in ascii_values:
        max=max+x
    if max > 200:
        max=max%200
    for index, values in enumerate(image):
        image[index] = values ^ max
 
    fin = open("mini_project_app/static/encrypted_image/"+name, 'wb')
    fin.write(image)
    fin.close()
    Messages.objects.create(sender_email=sm,receiver_email=rm,roomcode=roomcode,encrypted_img_path="static/encrypted_image/"+name,sender_name=User.objects.get(email=sm).name,receiver_name=User.objects.get(email=rm).name,message="",encrypted_img_name=name,key=key)
    return redirect('home')

def decrypt(request):
    return render(request,'decrypt.html')

decryptedimagename =""
def decryptimage(request):
    img=request.FILES['img']
    key=request.POST['key']
    name=img.name
    name_change=''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(30))
    name=name_change+"_"+name
    file_name = FileSystemStorage().save("mini_project_app/static/encrypted_image/"+name, img)
    fin = open("mini_project_app/static/encrypted_image/"+name, 'rb')
    image = fin.read()
    fin.close()
    image = bytearray(image)
    ascii_values = [ord(character) for character in key]
    max=0
    for x in ascii_values:
        max=max+x
    if max > 200:
        max=max%200
    for index, values in enumerate(image):
        image[index] = values ^ max
    fin = open("mini_project_app/static/encrypted_image/"+name, 'wb')
    fin.write(image)
    fin.close()
    global decryptedimagename
    decryptedimagename = name
    return redirect('download_decrypted_image/'+name)

def download_decrypted_image(request,name):
    return render(request,'download_decrypted_image.html',{'name':"../static/encrypted_image/"+name})


# User Signup / Login / Logout
def signup(request):
    return render(request,'signup.html')

def signup_user(request):
    username=request.POST['username']
    email=request.POST['email']
    pwd=request.POST['pwd']
    if User.objects.filter(email=email).exists():
            messages.info(request,'User Already Exists !')
            return redirect('signup')
    else:
            global otp
            otp=''.join([str(random.randint(0, 999)).zfill(3) for _ in range(2)])
            message="OTP : "+otp + "\n If you didn't did this please ignore this"
            reciever=[str(email)]
            subject="OTP for Encryptex"
            send_mail(subject,message,os.environ.get('EMAIL'),reciever)
            return render(request,'otp.html',{'username':username,'email':email,'pwd':pwd})

def otpcheck(request):
    otp_provided=request.POST['otp']
    username=request.POST['username']
    email=request.POST['email']
    pwd=request.POST['pwd']
    global otp
    if otp == otp_provided:
        print(pwd)
        pwd=sha512.hash(pwd, rounds=5000,salt=os.environ.get('SALT'))
        email=email.lower()
        User.objects.create(name=username,password=pwd,email=email,private_key="nill")
        return redirect('login')
    else :
        messages.info(request,'Wrong OTP !')
        return redirect('signup')


def login_user(request):
    email=request.POST['email']
    pwd1=request.POST['pwd']
    email=email.lower()
    if User.objects.filter(email=email).exists():
        user=User.objects.get(email=email)
        password_verify=user.password
        print(pwd1)
        pwd1=sha512.hash(pwd1, rounds=5000,salt=os.environ.get('SALT'))
        print(pwd1)
        print(password_verify)
        if pwd1==password_verify:
            privatekey=''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(30))
            request.session['private_mini_project_key']=privatekey
            user.private_key=privatekey
            user.save()
            return redirect('home')
        else:
            messages.info(request,'Wrong Password !')
            return redirect('login')
    else:
        messages.info(request,'User Does Not Exists !')
        return redirect('login')
    
def login(request):
    return render(request,'index.html')

def logout(request):
    try:
        del request.session['private_mini_project_key']
    except KeyError:
        pass
    return redirect('login')

def forgot_password(request):
    return render(request,'forgot_password.html')

def email_check(request):
    email=request.POST['email']
    email=email.lower()
    print(email)
    if User.objects.filter(email=email).exists():
            global otp_forgot_password
            otp_forgot_password=''.join([str(random.randint(0, 999)).zfill(3) for _ in range(2)])
            message="OTP For Password change : "+otp_forgot_password + "\n If you don't wish to reset your password, disregard this email and no action will be taken."
            reciever=[str(email)]
            subject="OTP for Password Reset in Encryptex"
            send_mail(subject,message,os.environ.get('EMAIL'),reciever)
            return render(request,'otp_forgot_password.html',{'email':email})
    else:
        messages.info(request,'User Doesn\'t Exists !')
        return redirect('login')

def otp_check_forgot_password(request):
    otp_provided=request.POST['otp']
    email=request.POST['email']
    email=email.lower()
    global otp_forgot_password
    if otp_forgot_password == otp_provided:
        return render(request,'newpassword.html',{'email':email})
    else :
        messages.info(request,'Wrong OTP !')
        return redirect('forgot_password')

def change_password(request):
    email=request.POST['email']
    email=email.lower()
    pwd=request.POST['password']
    cpwd=request.POST['cpwd']
    pwd=sha512.hash(pwd, rounds=5000,salt=os.environ.get('SALT'))
    User.objects.filter(email=email).update(password=pwd)
    messages.info(request,'Password Changed Successfull !')
    return redirect('login')

