from django.db import models

# Create your models here.
class User(models.Model):
    name=models.CharField(max_length=100)
    password=models.CharField(max_length=300)
    email=models.CharField(max_length=100)
    private_key=models.CharField(max_length=100)

class Talker(models.Model):
    sender_email=models.CharField(max_length=100)
    sender_name=models.CharField(max_length=100)
    receiver_email=models.CharField(max_length=100)
    receiver_name=models.CharField(max_length=100)
    # Tells if there is a new message in the chat
    new_message=models.BooleanField(default=False)
    # Stores new message
    last_message=models.CharField(max_length=10000,default="")
    roomcode=models.CharField(max_length=100)

    

class Messages(models.Model):
    sender_email=models.CharField(max_length=100)
    sender_name=models.CharField(max_length=100)
    receiver_email=models.CharField(max_length=100)
    receiver_name=models.CharField(max_length=100)
    message=models.CharField(max_length=10000)
    roomcode=models.CharField(max_length=100)
    encrypted_img_path=models.CharField(max_length=100,default="nill")
    key=models.CharField(max_length=100,default="nill")
    encrypted_img_name=models.CharField(max_length=100,default="nill")

