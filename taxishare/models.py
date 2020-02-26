from django.db import models
from django.core.mail import send_mail
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.conf import settings

import pandas as pd
import random, string


class CustomUserManager(UserManager):
    """
    ユーザーマネージャー
    """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        ユーザー情報のベースを設定する。
        """
        if not email:
            raise ValueError('メールアドレスは必須です。')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        利用者情報を設定する。
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        管理者情報を設定する。
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('管理者はis_staff=Trueが必須です。')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('管理者はis_superuser=Trueが必須です。')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    カスタムユーザーモデル
    usernameを使わず、emailアドレスをユーザー名として使う。
    """
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    # 生年月日
    birth_date = models.DateField('生年月日',null=True)
    # 性別
    sex = models.IntegerField('性別',null=True)
    # 出発地（今回は固定値）
    origin_latitude = models.FloatField('出発地の緯度', default=35.696739)
    origin_longitude = models.FloatField('出発地の経度', default=139.814484)
    # 目的地
    desitination_latitude = models.FloatField('目的地の緯度', null=True)
    desitination_longitude = models.FloatField('目的地の経度', null=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'ユーザーが管理サイトにログインするかどうか指定する。'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'ユーザーがアクティブとするかどうか指定する。'
            'アカウントを削除する代わりに選ばない。'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        """
        苗字　名前
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        苗字
        """
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        メール送信する
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def username(self):
        return self.email


class Taxi(models.Model):
    """
    タクシーの配車情報を設定する。
    """
    # ユーザー
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    #タクシーの配車番号
    number = models.IntegerField(_('number'))

    class Meta:
        verbose_name = 'タクシー'
        verbose_name_plural = 'タクシー'

    def __str__(self):
        return self.user.email
