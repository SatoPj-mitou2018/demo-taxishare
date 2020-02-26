from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _
from .models import User, Taxi
from django import forms


SEX_CHOICES = [
(-1, '男性'),
(1, '女性'),
]


class MyUserChangeForm(UserChangeForm):
    sex = forms.ChoiceField(label='性別', choices=SEX_CHOICES)

    class Meta:
        model = User
        fields = '__all__'


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email',)


class MyUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': (
        'first_name', 'last_name', 'birth_date', 'sex',
        'origin_latitude', 'origin_longitude',
        'desitination_latitude', 'desitination_longitude'
        )}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email', 'first_name', 'last_name', 'birth_date', 'sex')
    ordering = ('email',)


admin.site.register(User, MyUserAdmin)
admin.site.register(Taxi)
