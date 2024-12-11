# yourapp/cron.py


from .models import User
from django.utils import timezone
from .models import Post
from django.shortcuts import get_object_or_404
import random
from .models import Category
import requests
import time


motivational_phrases = [
    "Jangan pernah berhenti, meski terasa sulit. Semua perjuangan ada hasilnya.",
    "Kamu kuat lebih dari yang kamu sadari, ayo bangkit!",
    "Kalah sekali nggak apa-apa, yang penting jangan berhenti berusaha.",
    "Semua orang punya masalah, tapi hanya yang kuat yang bisa melewatinya.",
    "Gagal itu biasa, yang penting adalah kembali mencoba.",
    "Jangan tunggu motivasi datang, bangkit dan buatlah sendiri.",
    "Setiap detik adalah kesempatan untuk memulai lagi.",
    "Hidup itu nggak selalu mudah, tapi percayalah, kamu bisa menghadapinya.",
    "Kadang, yang kamu butuhkan cuma sedikit keberanian untuk mulai.",
    "Jangan takut gagal, karena di balik kegagalan ada pelajaran berharga.",
    "Biarpun lambat, yang penting jangan berhenti.",
    "Mimpi nggak akan tercapai kalau cuma diimpikan. Ayo action!",
    "Kerja keras hari ini, hasil manis di masa depan.",
    "Jangan khawatir tentang langkah kecilmu, asalkan kamu terus melangkah.",
    "Hari-hari buruk cuma sementara, tapi hasil baiknya akan bertahan selamanya.",
    "Setiap rintangan adalah peluang untuk jadi lebih kuat.",
    "Keberhasilan itu bukan soal seberapa cepat kamu sampai, tapi seberapa tahan kamu berjuang.",
    "Jangan lihat seberapa jauh jalan yang harus ditempuh, fokus saja pada langkah pertama.",
    "Terkadang hal terbaik dalam hidup datang setelah kesulitan terbesar.",
    "Coba lagi, coba terus! Dunia butuh versi terbaik dari dirimu."
]


def generate_motivational_quote():
    words = random.sample(motivational_phrases, 20)
    quote = " ".join(words)
    word_count = len(quote.split())
    if word_count > 20:
        quote = " ".join(quote.split()[:20])

    return quote

def create_midnight_post():
    print("hit cron job create_minute_post")
    print("Waktu sekarang di Jakarta: It's midnight!")
    data = ''
    url = 'https://api.ryzendesu.vip/api/ai/claude'
    params = {
        'text': f'buatkan kata2 untuk motivasi maksimal 20 kata ,dengan bahasa jaksel,agar ngena di hati, {generate_motivational_quote()}',
        'timestamp': time.time(),
        'random': random.randint(1, 1000)
    }
    headers = {'accept': 'application/json'}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
    else:
        print(f"Error: {response.status_code}")
    print(data.get('response', 'No response data'))
    target_email = 'aigaul@learnsosmed.com'
    user = get_object_or_404(User, email=target_email)
    category = get_object_or_404(Category, id=2)
    new_post = Post.objects.create(
        creator=user,
        caption=data['response'],
        categories=category
    )

    print(f"Post by AI created at {timezone.now()}")



def create_every_minute_post():
    print("hit cron job create_minute_post")
    print("Waktu sekarang di Jakarta: It's midnight!")
    data = ''
    url = 'https://api.ryzendesu.vip/api/ai/claude'
    params = {
        'text': f'buatkan kata2 untuk motivasi maksimal 20 kata ,dengan bahasa jaksel,agar ngena di hati, {generate_motivational_quote()}',
        'timestamp': time.time(),
        'random': random.randint(1, 1000)
    }
    headers = {'accept': 'application/json'}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
    else:
        print(f"Error: {response.status_code}")
    print(data.get('response', 'No response data'))
    target_email = 'aigaul@learnsosmed.com'
    user = get_object_or_404(User, email=target_email)
    category = get_object_or_404(Category, id=2)
    new_post = Post.objects.create(
        creator=user,
        caption=data['response'],
        categories=category
    )

    print(f"Post by AI created at {timezone.now()}")


