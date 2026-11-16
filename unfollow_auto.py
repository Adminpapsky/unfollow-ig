# unfollow_auto.py
"""
Versi perbaikan:
- Tidak mengirim username/password Instagram ke Telegram atau layanan lain.
- Meminta kredensial satu kali saja.
- Menghentikan proses dengan aman jika Instagram membatasi permintaan (HTTP 429).
- Tidak menjalankan unfollow jika pengambilan following/followers gagal.
- Tidak melakukan retry otomatis saat terkena pembatasan.
"""

import getpass
import os
import random
import sys
import time

from instagrapi import Client
from instagrapi.exceptions import (
    TwoFactorRequired,
    PleaseWaitFewMinutes,
    FeedbackRequired,
    ChallengeRequired,
    LoginRequired,
    RateLimitError,
    ClientThrottledError,
)

# ===== PENGATURAN =====
CREATOR = "itsme.cuya"
PER_HARI = 3  # Mulai dari jumlah kecil; ubah sendiri setelah memahami risikonya.
JEDA = (5, 20)
WHITELIST = {"akun_a", "akun_b"}
WAJIB_FOLLOW_CREATOR = True
# ======================

DONE_ID = "sudah_unfollow_id.txt"
DONE_LAMA = "sudah_unfollow.txt"
SESSION_FILE = "session.json"


def berhenti(pesan, kode=1):
    print(f"\n{pesan}")
    raise SystemExit(kode)


def load_set(path):
    if not os.path.exists(path):
        return set()
    with open(path, "r", encoding="utf-8") as file:
        return {line.strip() for line in file if line.strip()}


def login_instagram(cl):
    username = input("Username Instagram: ").strip()
    password = getpass.getpass("Password (tidak terlihat saat diketik): ")

    try:
        cl.login(username, password)
    except TwoFactorRequired:
        kode = input("Masukkan kode 2FA: ").strip()
        cl.login(username, password, verification_code=kode)
    except (PleaseWaitFewMinutes, FeedbackRequired, ChallengeRequired,
            LoginRequired, RateLimitError, ClientThrottledError):
        berhenti(
            "Login ditolak atau dibatasi Instagram. Hentikan percobaan dan "
            "periksa aplikasi Instagram sebelum mencoba lagi."
        )

    # File sesi berisi data autentikasi. Jangan dibagikan atau diunggah ke GitHub.
    cl.dump_settings(SESSION_FILE)


def ambil_data_relasi(cl, user_id):
    print("Mengambil daftar following & followers terbaru...")

    try:
        following = cl.user_following(user_id)
        followers = cl.user_followers(user_id)
    except (ClientThrottledError, PleaseWaitFewMinutes, RateLimitError) as exc:
        berhenti(
            "Instagram sedang membatasi permintaan (HTTP 429/rate limit).\n"
            "Tidak ada akun yang di-unfollow dan data parsial tidak akan dipakai.\n"
            "Tutup script, tunggu sampai pembatasan berakhir, lalu coba lagi "
            "nanti secara manual. Script tidak akan mengulang permintaan otomatis.\n"
            f"Detail: {type(exc).__name__}"
        )
    except (ChallengeRequired, LoginRequired, FeedbackRequired) as exc:
        berhenti(
            "Instagram meminta verifikasi atau sesi login perlu diperiksa. "
            "Tidak ada akun yang di-unfollow.\n"
            f"Detail: {type(exc).__name__}"
        )
    except Exception as exc:
        berhenti(
            "Gagal mengambil daftar following/followers. Tidak ada akun yang "
            "di-unfollow. Periksa koneksi dan coba lagi nanti.\n"
            f"Detail: {type(exc).__name__}: {exc}"
        )

    # Normalisasi ID untuk mencegah perbandingan int vs string yang keliru.
    following = {str(uid): user for uid, user in following.items()}
    follower_ids = {str(uid) for uid in followers.keys()}
    return following, follower_ids


def main():
    cl = Client()
    cl.delay_range = [2, 5]

    login_instagram(cl)

    me = str(cl.user_id)
    following, follower_ids = ambil_data_relasi(cl, me)
    print(f"Following: {len(following)} | Followers: {len(follower_ids)}")

    # Verifikasi akun pembuat. Jika tidak dapat diverifikasi, hentikan bila diwajibkan.
    creator_id = None
    try:
        creator_id = str(cl.user_id_from_username(CREATOR))
    except Exception as exc:
        print(f"Tidak dapat memverifikasi akun @{CREATOR}: {type(exc).__name__}")
        if WAJIB_FOLLOW_CREATOR:
            berhenti("Verifikasi akun pembuat gagal. Tidak ada akun yang di-unfollow.")

    if creator_id and creator_id != me:
        already_follows = creator_id in following
        if already_follows:
            print(f"Kamu sudah follow @{CREATOR}. Terima kasih!")
        else:
            print("\nScript ini dibuat oleh @{0}.".format(CREATOR))
            answer = input(f"Follow @{CREATOR}? (y/n): ").strip().lower()
            if answer == "y":
                try:
                    cl.user_follow(creator_id)
                    print(f"Permintaan follow @{CREATOR} berhasil dikirim.")
                except Exception as exc:
                    print(f"Gagal follow @{CREATOR}: {type(exc).__name__}: {exc}")
                    if WAJIB_FOLLOW_CREATOR:
                        berhenti("Follow akun pembuat gagal. Tidak ada unfollow yang dilakukan.")
            elif WAJIB_FOLLOW_CREATOR:
                berhenti("Syarat follow akun pembuat belum dipenuhi. Dihentikan.")

    done_ids = load_set(DONE_ID)
    done_names = {name.lower() for name in load_set(DONE_LAMA)}
    whitelist = {name.lower() for name in WHITELIST} | {CREATOR.lower()}

    targets = [
        (uid, user.username)
        for uid, user in following.items()
        if uid not in follower_ids
        and uid not in done_ids
        and uid != creator_id
        and user.username
        and user.username.lower() not in whitelist
        and user.username.lower() not in done_names
    ]

    print(f"Target tidak follback: {len(targets)}")
    if not targets:
        print("Tidak ada target yang perlu diproses.")
        return

    confirm = input(
        f"Akan mencoba unfollow maksimal {PER_HARI} akun. Lanjutkan? (y/n): "
    ).strip().lower()
    if confirm != "y":
        print("Dibatalkan. Tidak ada akun yang di-unfollow.")
        return

    success = 0
    for uid, username in targets:
        if success >= PER_HARI:
            break

        try:
            result = cl.user_unfollow(uid)
            if result:
                success += 1
                print(f"[{success}] unfollow @{username}")
                with open(DONE_ID, "a", encoding="utf-8") as file:
                    file.write(uid + "\n")
                time.sleep(random.randint(*JEDA))
            else:
                print(f"Gagal @{username}; Instagram tidak mengonfirmasi tindakan.")
                time.sleep(random.randint(3, 6))
        except (PleaseWaitFewMinutes, FeedbackRequired, ChallengeRequired,
                LoginRequired, RateLimitError, ClientThrottledError) as exc:
            print(
                "Instagram membatasi tindakan atau meminta verifikasi. "
                "Proses dihentikan; jangan jalankan ulang berulang kali. "
                f"Detail: {type(exc).__name__}"
            )
            break
        except Exception as exc:
            print(f"Gagal @{username}: {type(exc).__name__}: {exc}")
            break

    print(f"Selesai. Berhasil unfollow: {success}.")


if __name__ == "__main__":
    main()
