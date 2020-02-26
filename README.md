# demo-taxishare
2018年度未踏ターゲット事業（アニーリング部門）採択プロジェクト「アニーリングマシンを利用したライドシェア支援アプリ」で作成した、サンプルWebアプリケーションです。

## Demo

## Requirement
* Python 3.7.6
* Django 3.0.3
* Pandas 1.0.1
* NumPy 1.18.1
* Requests 2.22.0
* SciPy 1.4.1
* Django-Pandas 0.6.1

## Usage
```
python manage.py migrate
python manage.py makemigrations taxishare
python manage.py createsuperuser
python manage.py runserver
```