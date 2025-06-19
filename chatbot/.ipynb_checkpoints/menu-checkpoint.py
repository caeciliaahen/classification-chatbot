from chatbot.routing import handle_intent, exit_keywords

def handle_menu():
    print("Ada yang bisa dibantu?")
    while True:
        user_input = input("").strip()
        if not user_input:
            continue
        if user_input in exit_keywords:
            print("Baik, terima kasih telah menggunakan layanan Halovet. Semoga hewan peliharaan Anda sehat selalu!")
            break
        if handle_intent(user_input):
            break