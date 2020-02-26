from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
)
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, resolve_url
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import generic
from .forms import (
    LoginForm, UserCreateForm, UserUpdateForm, MyPasswordChangeForm,
    MyPasswordResetForm, MySetPasswordForm, EmailChangeForm,
    PlaceUpdateForm
)
from .models import Taxi

from django_pandas.io import read_frame

from taxishare.anneal import main


User = get_user_model()


class Top(generic.TemplateView):
    """
    トップページを表示する。
    """
    template_name = 'taxishare/top.html'


class Login(LoginView):
    """
    ログインページを表示する。
    """
    template_name = 'taxishare/login.html'
    form_class = LoginForm


class Logout(LogoutView):
    """
    ログアウトページを表示する。
    """
    template_name = 'taxishare/top.html'

class UserCreate(generic.CreateView):
    """
    ユーザー仮登録ページを表示する。
    """
    template_name = 'taxishare/user_create.html'
    form_class = UserCreateForm

    def form_valid(self, form):
        """
        仮登録と本登録用メールの発行を行う。
        """
        user = form.save(commit=False)
        user.is_active = False  # 仮登録
        user.save()

        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }
        subject = render_to_string('taxishare/mail_template/create/subject.txt', context).strip()
        message = render_to_string('taxishare/mail_template/create/message.txt', context).strip()
        user.email_user(subject, message)
        return redirect('taxishare:user_create_done')


class UserCreateDone(generic.TemplateView):
    """
    ユーザーの仮登録を完了する。
    """
    template_name = 'taxishare/user_create_done.html'


class UserCreateComplete(generic.TemplateView):
    """
    メール内URLアクセス後に、ユーザーを本登録する。
    """
    template_name = 'taxishare/user_create_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)  # 1日以内

    def get(self, request, **kwargs):
        """
        tokenが正しければ本登録を行う。
        """
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)
        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()
        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()
        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            # ユーザーが仮登録されていない
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                # まだ仮登録で、他に問題なければ本登録とする
                if not user.is_active:
                    user.is_active = True
                    user.save()
                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()


class OnlyYouMixin(UserPassesTestMixin):
    """
    本人か管理者だけユーザーページアクセスを許可する。
    """
    raise_exception = True

    def test_func(self):
        """
        本人か管理者かどうか確認する。
        """
        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_superuser


class UserDetail(OnlyYouMixin, generic.DetailView):
    """
    ユーザーの詳細ページを表示する。
    """
    model = User
    template_name = 'taxishare/user_detail.html'


class UserUpdate(OnlyYouMixin, generic.UpdateView):
    """
    ユーザー情報更新ページを表示する。
    """
    template_name = 'taxishare/user_form.html'
    model = User
    form_class = UserUpdateForm

    def get_success_url(self):
        """
        ユーザー情報更新ページのURLを返す。
        """
        return resolve_url('taxishare:user_detail', pk=self.kwargs['pk'])


class PasswordChange(PasswordChangeView):
    """
    パスワード変更ページを表示する。
    """
    template_name = 'taxishare/password_change.html'
    form_class = MyPasswordChangeForm
    success_url = reverse_lazy('taxishare:password_change_done')


class PasswordChangeDone(PasswordChangeDoneView):
    """
    パスワード変更完了ページを表示する。
    """
    template_name = 'taxishare/password_change_done.html'


class PasswordReset(PasswordResetView):
    """
    パスワード変更用URLの送付ページを表示する。
    """
    template_name = 'taxishare/password_reset_form.html'
    form_class = MyPasswordResetForm
    success_url = reverse_lazy('taxishare:password_reset_done')
    subject_template_name = 'taxishare/mail_template/password_reset/subject.txt'
    email_template_name = 'taxishare/mail_template/password_reset/message.txt'


class PasswordResetDone(PasswordResetDoneView):
    """
    パスワード変更用URLの送信完了ページを表示する。
    """
    template_name = 'taxishare/password_reset_done.html'


class PasswordResetConfirm(PasswordResetConfirmView):
    """
    新パスワード入力ページを表示する。
    """
    template_name = 'taxishare/password_reset_confirm.html'
    form_class = MySetPasswordForm
    success_url = reverse_lazy('taxishare:password_reset_complete')


class PasswordResetComplete(PasswordResetCompleteView):
    """
    新パスワード設定完了ページを表示する。
    """
    template_name = 'taxishare/password_reset_complete.html'


class EmailChange(LoginRequiredMixin, generic.FormView):
    """
    メールアドレス変更ページを表示する。
    """
    template_name = 'taxishare/email_change_form.html'
    form_class = EmailChangeForm

    def form_valid(self, form):
        """
        メールアドレス変更用URLを送付する。
        """
        user = self.request.user
        new_email = form.cleaned_data['email']

        # URLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'token': dumps(new_email),
            'user': user,
        }
        subject = render_to_string('taxishare/mail_template/email_change/subject.txt', context).strip()
        message = render_to_string('taxishare/mail_template/email_change/message.txt', context).strip()
        send_mail(subject, message, None, [new_email])
        return redirect('taxishare:email_change_done')


class EmailChangeDone(LoginRequiredMixin, generic.TemplateView):
    """
    メールアドレスの変更用URLの送付完了ページを表示する。
    """
    template_name = 'taxishare/email_change_done.html'


class EmailChangeComplete(LoginRequiredMixin, generic.TemplateView):
    """
    メール内URLにアクセス後、メールアドレスを変更する。"""
    template_name = 'taxishare/email_change_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        """
        tokenが正しければ変更を行う。
        """
        token = kwargs.get('token')
        try:
            new_email = loads(token, max_age=self.timeout_seconds)
        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()
        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()
        # tokenは問題なし
        else:
            User.objects.filter(email=new_email, is_active=False).delete()
            request.user.email = new_email
            request.user.save()
            return super().get(request, **kwargs)


class PlaceUpdate(OnlyYouMixin, generic.UpdateView):
    """
    地点情報更新ページ（利用者側検索ページ）を表示する。
    """
    template_name = 'taxishare/place_update.html'
    form_class = PlaceUpdateForm
    model = User

    def get_success_url(self):
        """
        地点情報更新完了ページ（利用者側検索中ページ）に飛ぶ。
        """
        return resolve_url('taxishare:place_update_done', pk=self.kwargs['pk'])


class PlaceUpdateDone(OnlyYouMixin, generic.TemplateView):
    """
    地点情報更新完了ページ（利用者側検索中ページ）を表示する。
    """
    template_name = 'taxishare/place_update_done.html'


class TaxiSearch(OnlyYouMixin, generic.ListView):
    """
    検索処理を行う。
    """
    template_name = 'taxishare/taxi_search.html'
    model = User

    def post(self, request, *args, **kwargs):
        """
        アニーリング処理を行い、配車番号を決定し、データベースを更新する。
        """
        #　user_tableを読み込み、pandas.dataframeに
        user_table = User.objects.filter(is_staff=False)  # user_tableの読み込み
        cols = ['id', 'desitination_latitude', 'desitination_longitude', 'sex', 'birth_date']  # 抽出するカラム
        df_of_user_table = read_frame(user_table, fieldnames=cols)  #データベースをpandas.dataframe化

        # アニーリング処理
        number_list = main.main(df_of_user_table)  # user_id順の配車番号が返ってくる

        # taxi_tableを更新
        Taxi.objects.all().delete()  # 既存taxi_tableのレコード削除
        taxis = []
        user_id_list = df_of_user_table['id'].values.tolist()  # user_tableのidリストを取得
        for i, user_id in enumerate(user_id_list):
            taxi = Taxi(user_id=user_id, number=number_list[i])
            taxis.append(taxi)
        Taxi.objects.bulk_create(taxis) # データベースにtaxi_tableを一括登録

        # メール送信
        for taxi in Taxi.objects.all():
            #send_result(obj)
            # メールの内容
            context = {
                'taxi': taxi,
            }
            subject = render_to_string('taxishare/mail_template/search/subject.txt', context).strip()
            message = render_to_string('taxishare/mail_template/search/message.txt', context).strip()
            send_mail(subject, message, None, [taxi.user.email])

        return redirect('taxishare:taxi_result', pk=self.kwargs['pk'])


class TaxiResult(OnlyYouMixin, generic.ListView):
    """
    タクシーの配車結果一覧ページを表示する。
    """
    template_name = 'taxishare/taxi_result.html'
    model = Taxi
