from django import forms    # База всех форм
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm  # Готовые формы регистрации и входа
# from .models import CustomUser  # кастомная модель пользователя
from django.contrib.auth import get_user_model  # получить текущую модель пользователя

from django.contrib.auth import password_validation  # импортируем модуль для валидации паролей
from django.core.exceptions import ValidationError # Исключение для валидации
from django.core.validators import MinLengthValidator  # Минимальная длина
from .validators import name_validator

from django.utils.translation import gettext_lazy as _  # Перевод сообщений
from django.utils.html import strip_tags  # Очистка HTML из полей
from django.core.validators import RegexValidator  # Валидация по регулярке



User = get_user_model()  # получаем модель пользователя

class CustomUserCreationForm(UserCreationForm): # → получает готовую логику хеширования пароля и проверки совпадения
    # переопределение полей
    email = forms.EmailField(
        required=True,
        max_length=66,
        widget=forms.EmailInput(attrs={'class': 'input-register form-control', 'placeholder': 'Your email'})
    )
    first_name = forms.CharField(
        validators=[
            name_validator,      # кастомный валидатор
            MinLengthValidator(2) # встроенный валидатор
        ],
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'input-register form-control', 'placeholder': 'Your first name'})
    )
    last_name = forms.CharField(
        validators=[
            name_validator,      
            MinLengthValidator(2)
        ],
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'input-register form-control', 'placeholder': 'Your last name'})
    )
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'input-register form-control', 'placeholder': 'Your password'})
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'input-register form-control', 'placeholder': 'Confirm your password'})
    )
    marketing_consent1 = forms.BooleanField(
        required=False,
        label="I agree to receive commercial, promotional, and marketing communications.",
        widget=forms.CheckboxInput(attrs={'class': 'checkbox-input-register'})
    )
    marketing_consent2 = forms.BooleanField(
        required=False,
        label="I agree to receive personalized commercial communications.",
        widget=forms.CheckboxInput(attrs={'class': 'checkbox-input-register'})
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',
                  'marketing_consent1', 'marketing_consent2')

    # защитить от дубликатов email
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email

    # для доп. данных в модели
    def save(self, commit=True):
        user = super().save(commit=False)  # → объект создан, но ещё не сохранён в БД
        # user.username = None
        user.marketing_consent1 = self.cleaned_data['marketing_consent1']
        user.marketing_consent2 = self.cleaned_data['marketing_consent2']
        if commit:
            user.save()
        return user
    

# Позволяем пользователю войти, используя email и пароль.
class CustomUserLoginForm(AuthenticationForm):   # → получает готовую логику аутентификации.
    username = forms.CharField( # Django всё равно называет его username в формах
        label='Email',
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'input-register form-control', 'placeholder': 'Your email'})
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'input-register form-control', 'placeholder': 'Your Password'})
    )
    

#  редактирование профиля
class CustomUserUpdateForm(forms.ModelForm): # → значит, автоматически связана с моделью
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'input-register form-control', 'placeholder': 'Your phone number'})
    )
    first_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'input-register form-control', 'placeholder': 'Your first name'})
    )
    last_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'input-register form-control', 'placeholder': 'Your last name'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'input-register form-control', 'placeholder': 'Your email'})
    )


    class Meta:
        model = User
        #  перечислены поля, которые можно редактировать.
        fields = ('first_name', 'last_name', 'email', 'address1', 'address2',
                  'city', 'country', 'province', 'postal_code', 'phone')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'input-register form-control', 
                                             'placeholder': 'Your email'}),
            'first_name': forms.TextInput(attrs={'class': 'input-register form-control', 
                                                 'placeholder': 'Your first name'}),
            'last_name': forms.TextInput(attrs={'class': 'input-register form-control', 
                                                'placeholder': 'Your last name'}),
            'address1': forms.TextInput(attrs={'class': 'input-register form-control', 
                                               'placeholder': 'Address line 1'}),
            'address2': forms.TextInput(attrs={'class': 'input-register form-control', 
                                               'placeholder': 'Address line 2'}),
            'city': forms.TextInput(attrs={'class': 'input-register form-control', 
                                           'placeholder': 'Your city'}),
            'country': forms.TextInput(attrs={'class': 'input-register form-control', 
                                              'placeholder': 'Your country'}),
            'province': forms.TextInput(attrs={'class': 'input-register form-control', 
                                               'placeholder': 'Your province'}),
            'postal_code': forms.TextInput(attrs={'class': 'input-register form-control', 
                                                  'placeholder': 'Your postal code'}),
        }

    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('This email is already in use.')
        return email
    

    def clean(self):
        cleaned_data = super().clean()
        # восстановление email, если поле пустое
        if not cleaned_data.get('email'):
            cleaned_data['email'] = self.instance.email

        # очистка HTML-тегов из текстовых полей
        for field in ['address1', 'address2', 'city', 'country', 'province',
                        'postal_code', 'phone']:
            if cleaned_data.get(field):
                cleaned_data[field] = strip_tags(cleaned_data[field])

        return cleaned_data