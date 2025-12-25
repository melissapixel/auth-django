from django.db import models
from django.contrib.auth.models import AbstractBaseUser # «голая» модель пользователя
from django.contrib.auth.models import PermissionsMixin # для прав доступа
from django.contrib.auth.models import BaseUserManager # менеджер для создания пользователей
# from django.contrib.auth.models import AbstractUser # базовая модель пользователя с полями
from django.utils.html import strip_tags # для очистки HTML-тегов из строки

class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)

        user = self.model(email=email, first_name=first_name, 
                          last_name=last_name,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return user


    def create_superuser(self, email, first_name, last_name, 
                         password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, first_name, 
                                 last_name, password, **extra_fields)
    

# Create your models here.
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=254)  # делаем email уникальным
    first_name = models.CharField(max_length=66)
    last_name = models.CharField(max_length=66)
    
    address1 = models.CharField(max_length=128, 
                                blank=True)  # позволяет оставлять поле пустым
    address2 = models.CharField(max_length=128, blank=True)
    city = models.CharField(max_length=64, blank=True)
    country = models.CharField(max_length=64, blank=True)
    province = models.CharField(max_length=64, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    
    marketing_consent1 = models.BooleanField(default=False) # example: sms
    marketing_consent2 = models.BooleanField(default=False) # example: email

    # username = models.CharField(max_length=150, unique=True, blank=True, null=True)

    # 🔑 Обязательные поля для AbstractBaseUser + PermissionsMixin
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()  # используем базовый менеджер пользователей

    # атрибуты модели пользователя
    USERNAME_FIELD = 'email'    # поле email как логин для входа
    REQUIRED_FIELDS = ['first_name', 'last_name']  # только при создании суперпользователя

    def __str__(self): 
        return self.email

    def clean(self):
        for field in ['address1', 'address2', 'city', 'country', 'province',
                            'postal_code', 'phone']:
            value = getattr(self, field)
            if value:
                setattr(self, field, strip_tags(value))
