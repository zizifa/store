from django.db import models
from django.contrib.auth.models import AbstractBaseUser , BaseUserManager
# Create your models here.

class AcoountsManager(BaseUserManager):
    def create_user(self,first_name,last_name,username,email,password=None):
        if not email:
            raise ValueError("you most have an email")
        if not username:
            raise ValueError("you most have a username")

        user = self.model(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self,first_name,last_name,username,email,password):
        user=self.create_user(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password
        )

        user.is_active=True
        user.is_staff=True
        user.is_superuser=True
        user.is_admin=True

        user.save(using=self._db)

class Accounts(AbstractBaseUser):
    first_name=models.CharField(max_length=50 , blank=True)
    last_name=models.CharField(max_length=50 , blank=True)
    username=models.CharField(max_length=50,unique=True)
    email=models.CharField(max_length=50 , unique=True ,blank=True)
    phone_number=models.CharField(max_length=20,unique=True)

    date_joined=models.DateTimeField(auto_now_add=True)
    last_login=models.DateTimeField(auto_now_add=True)
    is_admin=models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)
    is_active=models.BooleanField(default=False)
    is_superadmin=models.BooleanField(default=False)

    USERNAME_FIELD='email'
    REQUIRED_FIELDS = ["first_name", "last_name","username"]

    objects= AcoountsManager()

    def __str__(self):
        return self.email

    def has_perm(self,perm,obj=None):
        return self.is_admin

    def has_module_perms(self,add_label):
        return True

class Profile(models.Model):
    user=models.OneToOneField(Accounts,on_delete=models.CASCADE)
    addres=models.CharField(max_length=100,blank=True)
    city=models.CharField(max_length=20,blank=True)
    state=models.CharField(max_length=100,blank=True)


    def __str__(self):
        return self.user.first_name


    def full_address(self):
        return f'{self.city},{self.state},{self.addres}'