import re
from chatbot.context import session

def map_yesno(text: str) -> int:
    text = text.strip().lower()
    negative_patterns = r"\b(tidak|no|false|nggak|enggak|engga|ngga|nga|ndak|gak|ga|gatau|kurang tahu|belum)\b"
    positive_patterns = r"\b(ya|yes|true|iya|betul|benar|pernah|sudah)\b"
    if re.search(positive_patterns, text): return 1
    elif re.search(negative_patterns, text): return 0
    return -1

indonesia_num_map = {
    "nol": 0, "satu": 1, "dua": 2, "tiga": 3, "empat": 4, "lima": 5,
    "enam": 6, "tujuh": 7, "delapan": 8, "sembilan": 9, "sepuluh": 10,
    "sebelas": 11, "dua belas": 12, "tiga belas": 13, "empat belas": 14,
    "lima belas": 15, "enam belas": 16, "tujuh belas": 17, "delapan belas": 18,
    "sembilan belas": 19, "dua puluh": 20
}

def indo_word_to_num(text: str):
    return indonesia_num_map.get(text.strip().lower())

def parse_age_input(age_text: str):
    age_text = age_text.strip().lower()
    if "bulan" in age_text:
        return 0
    if "tahun" in age_text:
        match = re.search(r"(\d+)", age_text)
        if match: return int(match.group(1))
        num = indo_word_to_num(age_text.replace("tahun", "").strip())
        if num is not None: return num
    if age_text.isdigit(): return int(age_text)
    num = indo_word_to_num(age_text)
    return num

def handle_registration(on_complete=None):
    from chatbot.schedule import dummy_registration_lookup

    print("Baik, mohon dilengkapi informasi berikut untuk administrasi pendaftaran.")

    # Jika belum ada nama pemilik, tanya dulu dan cek apakah sudah pernah mendaftar
    if not session.get("owner_name"):
        print("Bisa dibantu, dengan siapa nama lengkap pemiliknya?")
        session["owner_name"] = input("").strip().title()

        print("Apakah sudah pernah mendaftar di klinik ini sebelumnya?")
        jawab = input("")
        if map_yesno(jawab) == 1:
            print("Bisa dibantu, untuk nomor HP yang sebelumnya terdaftar?")
            session["phone"] = input("").strip()
            dummy_registration_lookup(on_complete=on_complete)
            return
    else:
        print(f"Mau melanjutkan pendaftaran atas nama {session['owner_name']}?")
        if map_yesno(input("")) != 1:
            print("Bisa dibantu, dengan siapa nama lengkap pemiliknya?")
            session["owner_name"] = input("").strip().title()
            session.pop("pet_name", None)
            session.pop("phone", None)

    # Cek alamat dan telepon
    if not session.get("address"):
        print("Bisa dibantu, untuk alamat lengkapnya di mana?")
        session["address"] = input("").strip().title()

    if not session.get("phone"):
        print("Bisa dibantu, untuk nomor HP aktifnya berapa?")
        session["phone"] = input("").strip()

    # Data hewan
    if session.get("pet_name"):
        print(f"Mau melanjutkan pendaftaran untuk {session['pet_name']}?")
        if map_yesno(input("")) != 1:
            session.pop("pet_name", None)
            session.pop("animal_type", None)
            session.pop("age", None)
            session.pop("gender", None)

    if not session.get("pet_name"):
        print("Siapa nama hewan peliharaan yang mau berobat?")
        session["pet_name"] = input("").strip().title()

    # Tanya apakah hewan pernah diperiksa
    print(f"Apakah {session['pet_name']} sudah pernah diperiksa di klinik ini sebelumnya?")
    jawab = input("")
    if map_yesno(jawab) == 1:
        dummy_registration_lookup(on_complete=on_complete)
        return

    # Lengkapi info hewan
    if not session.get("animal_type"):
        print(f"Termasuk jenis hewan apakah {session['pet_name']}?")
        session["animal_type"] = input("").strip().lower()

    if session.get("age") is None:
        while True:
            print(f"Berapa umur {session['pet_name']} saat ini?")
            pet_age_raw = input("")
            pet_age = parse_age_input(pet_age_raw)
            if pet_age is not None:
                session["age"] = pet_age
                break
            print("Mohon masukkan umur seperti '1 tahun', '6 bulan', atau angka/tulisan yang valid.")

    if not session.get("gender"):
        print(f"Apakah {session['pet_name']} jantan atau betina?")
        while True:
            gender_input = input("").strip().lower()
            if gender_input in ["jantan", "betina", "pria", "wanita", "laki-laki", "perempuan"]:
                session["gender"] = "betina" if gender_input in ["betina", "wanita", "perempuan"] else "jantan"
                break
            print("Mohon jawab dengan 'jantan' atau 'betina'.")

    print(f"Pendaftaran akan dilanjutkan atas nama pemilik {session['owner_name']} untuk {session['pet_name']}.")
    print("Terima kasih, data akan kami proses.")
    dummy_registration_lookup(on_complete=on_complete)