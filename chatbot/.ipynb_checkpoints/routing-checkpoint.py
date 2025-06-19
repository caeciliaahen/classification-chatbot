from chatbot.diagnosis import handle_diagnosis
from chatbot.registration import handle_registration
from chatbot.schedule import dummy_schedule_lookup
import re

intent_keywords = {
    "diagnosis": ["konsultasi", "konsul", "periksa", "cek"],
    "schedule": ["jadwal", "praktek", "praktik", "kapan", "hari"],
    "register": ["daftar", "pendaftaran", "registrasi", "regis", "register"],
}

exit_keywords = {
    "tidak", "ga", "gak", "nggak", "enggak", "no", "engga", "cukup", "udah",
    "tidak ada", "nggak ada"
}

def detect_intent(user_input):
    text = user_input.lower()
    for intent, keywords in intent_keywords.items():
        if any(re.search(rf"\b{kw}\b", text) for kw in keywords):
            return intent
    return "unknown"

def handle_intent(user_input: str, on_complete=None) -> bool:
    intent = detect_intent(user_input)

    if intent == "diagnosis":
        handle_diagnosis(on_complete=on_complete)
        return True
    elif intent == "register":
        handle_registration(on_complete=on_complete)
        return True
    elif intent == "schedule":
        dummy_schedule_lookup(on_complete=on_complete)
        return True
    else:
        print("Maaf, saya belum memahami maksud Anda. Apakah ingin konsultasi, lihat jadwal dokter, atau melakukan pendaftaran?")
        return False