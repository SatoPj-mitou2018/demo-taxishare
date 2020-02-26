from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm, UserCreationForm, PasswordChangeForm,
    PasswordResetForm, SetPasswordForm
)
from django.contrib.auth import get_user_model


# 性別の選択肢
SEX_CHOICES = [
(-1, '男性'),
(1, '女性'),
]


User = get_user_model()


class EmailChangeForm(forms.ModelForm):
    """
    メールアドレス変更フォーム
    """
    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data['email']
        User.objects.filter(email=email, is_active=False).delete()
        return email


class LoginForm(AuthenticationForm):
    """
    ログインフォーム
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label  # placeholderにフィールドのラベルを入れる


class UserCreateForm(UserCreationForm):
    """
    ユーザー登録用フォーム
    """
    birth_date = forms.DateField(
        label='生年月日',
        widget=forms.SelectDateWidget(years=[x for x in range(1920, 2020)]),
    )
    sex = forms.ChoiceField(label='性別', choices=SEX_CHOICES)

    class Meta:
        model = User
        fields = ('email', 'birth_date', 'sex')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data['email']
        User.objects.filter(email=email, is_active=False).delete()
        return email


class UserUpdateForm(forms.ModelForm):
    """
    ユーザー情報更新フォーム
    """
    birth_date = forms.DateField(
        label='生年月日',
        widget=forms.SelectDateWidget(years=[x for x in range(1920, 2020)]),
    )
    sex = forms.ChoiceField(label='性別', choices=SEX_CHOICES)

    class Meta:
        model = User
        fields = ('last_name', 'first_name', 'birth_date', 'sex')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class MyPasswordChangeForm(PasswordChangeForm):
    """
    パスワード変更フォーム
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class MyPasswordResetForm(PasswordResetForm):
    """
    パスワード忘れたときのフォーム
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class MySetPasswordForm(SetPasswordForm):
    """
    パスワード再設定用フォーム(パスワード忘れて再設定)
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class PlaceUpdateForm(forms.ModelForm):
    """
    地点更新用フォーム
    """
    origin_latitude = forms.FloatField(label='出発地の緯度', initial=35.696739, disabled=True)
    origin_longitude = forms.FloatField(label='出発地の経度', initial=139.814484, disabled=True)
    desitination_latitude = forms.FloatField(label='目的地の緯度')
    desitination_longitude = forms.FloatField(label='目的地の経度')

    class Meta:
        model = User
        fields = ('origin_latitude', 'origin_longitude', 'desitination_latitude', 'desitination_longitude')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
