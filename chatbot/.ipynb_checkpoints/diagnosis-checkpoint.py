import os
import joblib
import re
import numpy as np
import pandas as pd
from datetime import datetime
from chatbot.registration import handle_registration
from chatbot.context import session

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
model = joblib.load(os.path.join(base_path, "app/model/rf_model.pkl"))
feature_names = joblib.load(os.path.join(base_path, "app/model/model_features.pkl"))
manual_maps = joblib.load(os.path.join(base_path, "app/model/manual_maps.pkl"))

label_map = {
    0: "infeksi bakteri",
    1: "penyakit klinis",
    2: "infeksi lainnya",
    3: "infeksi pernapasan",
    4: "infeksi virus"
}

def preprocess_input(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9\s]", "", text.strip().lower())

def map_yesno(text: str) -> int:
    text = preprocess_input(text)
    if re.search(r"\b(ya|yes|true|iya|betul|benar|ada|pernah)\b", text):
        return 1
    elif re.search(r"\b(tidak|no|false|nggak|nngak|enggak|engga|ngga|nga|ndak|gak|ga|tdk|gatau|kurang tahu|belum)\b", text):
        return 0
    return -1

bilingual_map = {
    "kucing": "cat", "anjing": "dog", "sapi": "cow", "kambing": "goat",
    "kuda": "horse", "babi": "pig", "kelinci": "rabbit", "domba": "sheep"
}

feature_questions = {
    "animal_type": "Termasuk jenis hewan apakah namahewan?",
    "nasal_discharge": "Apakah namahewan mengeluarkan cairan dari hidung?",
    "skin_lesions": "Apakah namahewan memiliki luka pada kulit?",
    "sneezing": "Apakah namahewan bersin-bersin?",
    "fever": "Apakah namahewan mengalami demam?",
    "lameness": "Apakah namahewan mengalami pincang?",
    "wool_issue": "Apakah namahewan mengalami masalah pada bulu?",
    "lethargy": "Apakah namahewan terlihat lesu?",
    "diarrhea": "Apakah namahewan mengalami diare?",
    "labored_breathing": "Apakah namahewan mengalami kesulitan bernapas?",
    "age": "Berapa usia namahewan?",
    "reduced_mobility": "Apakah pergerakan namahewan mengalami keterbatasan?",
    "dehydration": "Apakah namahewan mengalami dehidrasi?",
    "duration": "Sudah berapa hari namahewan mengalami gejala tersebut?",
    "weight_loss": "Apakah namahewan mengalami penurunan berat badan?",
    "milk_yield_issue": "Apakah produksi susu pada namahewan terganggu?"
}

indonesia_num_map = {
    "nol": 0, "satu": 1, "dua": 2, "tiga": 3, "empat": 4, "lima": 5,
    "enam": 6, "tujuh": 7, "delapan": 8, "sembilan": 9, "sepuluh": 10,
    "sebelas": 11, "dua belas": 12, "tiga belas": 13, "empat belas": 14,
    "lima belas": 15, "enam belas": 16, "tujuh belas": 17, "delapan belas": 18,
    "sembilan belas": 19, "dua puluh": 20
}

def indo_word_to_num(text):
    return indonesia_num_map.get(text.strip().lower())

def handle_diagnosis(on_complete=None):
    print("Baik, kita akan lanjut ke sesi konsultasi hewan peliharaan Anda.")

    user_input = {}

    if not session.get("pet_name"):
        print("Siapa nama hewan peliharaan Anda?")
        pet_name = preprocess_input(input(""))
        if not pet_name:
            print("Mohon isi nama hewan peliharaan.")
            return
        session["pet_name"] = pet_name.capitalize()
    else:
        print(f"Apakah ingin melanjutkan diagnosis untuk {session['pet_name']}?")
        jawaban = preprocess_input(input(""))
        if map_yesno(jawaban) == 0:
            print("Baik, kita akan melanjutkan diagnosis untuk hewan peliharaan yang lain.")
            print("Siapa nama hewan peliharaan yang mau berobat?")
            pet_name = preprocess_input(input(""))
            if not pet_name:
                print("Mohon isi nama hewan peliharaan.")
                return
            session["pet_name"] = pet_name.capitalize()
            session.pop("animal_type", None)
            session.pop("age", None)
            session.pop("gender", None)
        else:
            print(f"Melanjutkan diagnosis untuk {session['pet_name']}.")

    if not session.get("gender"):
        print(f"Apa {session['pet_name']} adalah jantan atau betina?")
        while True:
            gender = preprocess_input(input(""))
            if gender in ["jantan", "betina"]:
                session["gender"] = gender
                break
            print("Mohon masukkan 'jantan' atau 'betina'.")

    animal_type_map = manual_maps["Animal_Type"]

    for key in feature_names:
        if key == "milk_yield_issue" and session.get("gender") != "betina":
            user_input[key] = 0
            session[key] = 0
            continue

        pertanyaan = feature_questions.get(key, f"{key}?").replace("namahewan", session["pet_name"])

        if session.get(key) is not None:
            user_input[key] = session[key]
            print(f"(✓) {key.replace('_', ' ').capitalize()} sudah tersedia: {session[key]}")
            continue

        while True:
            print(pertanyaan)
            jawaban = preprocess_input(input(""))
            if not jawaban:
                print("Mohon isi jawaban terlebih dahulu.")
                continue

            if key == "animal_type":
                mapped_animal = bilingual_map.get(jawaban, jawaban).title()
                if mapped_animal in animal_type_map:
                    user_input[key] = animal_type_map[mapped_animal]
                    session[key] = animal_type_map[mapped_animal]
                    break
                else:
                    print("Jenis hewan tidak tersedia untuk diagnosis online.")
                    lanjut = preprocess_input(input("Mau mendaftar ke klinik?: "))
                    if map_yesno(lanjut) == 1:
                        handle_registration()
                    elif callable(on_complete):
                        on_complete()
                    return

            elif key == "age":
                if "bulan" in jawaban:
                    user_input[key] = 0
                    session[key] = 0
                    break
                match = re.search(r"(\d+)", jawaban)
                num = int(match.group(1)) if match else indo_word_to_num(jawaban.replace("tahun", "").strip())
                if num is not None:
                    user_input[key] = num
                    session[key] = num
                    break
                print("Masukkan usia dalam format angka, seperti '1 tahun' atau 'enam bulan'.")

            elif key == "duration":
                match = re.search(r"(\d+)", jawaban)
                if match:
                    user_input[key] = int(match.group(1))
                    break
                num = indo_word_to_num(jawaban)
                if num is not None:
                    user_input[key] = num
                    break
                print("Masukkan durasi gejala dalam hari, seperti '3' atau 'tiga'.")

            else:
                mapped = map_yesno(jawaban)
                if mapped != -1:
                    user_input[key] = mapped
                    session[key] = mapped
                    break
                print("Mohon jawab dengan 'ya' atau 'tidak'.")

    if set(user_input.keys()) != set(feature_names):
        print("Data belum lengkap. Ulangi sesi diagnosis?")
        retry = preprocess_input(input(""))
        if map_yesno(retry) == 1:
            return handle_diagnosis(on_complete=on_complete)
        elif callable(on_complete):
            on_complete()
        return

    X_df = pd.DataFrame([user_input]).reindex(columns=feature_names, fill_value=0)
    X_df.columns = model.feature_names_in_
    pred = model.predict(X_df)[0]
    label = label_map.get(pred, f"Label {pred}")
    session["diagnosis"] = label

    print(f"Berdasarkan gejala, kemungkinan besar {session['pet_name']} mengalami {label}.")

    log_df = X_df.copy()
    log_df["owner_name"] = session.get("owner_name", "-")
    log_df["pet_name"] = session["pet_name"]
    log_df["diagnosis"] = label
    log_df["timestamp"] = datetime.now().isoformat()
    log_path = os.path.join(base_path, "chatbot/chat_log.csv")
    log_df.to_csv(log_path, mode="a", header=not os.path.exists(log_path), index=False)

    print("Mau mendaftar untuk pemeriksaan di klinik?")
    lanjut = preprocess_input(input(""))
    if map_yesno(lanjut) == 1:
        handle_registration()
    elif callable(on_complete):
        on_complete()