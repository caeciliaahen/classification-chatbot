from chatbot.routing import handle_intent, exit_keywords

def handle_menu(first_time=True):
    while True:
        print("Apakah ada yang bisa dibantu?" if first_time else "Apakah masih ada lagi yang bisa dibantu?")
        first_time = False

        user_input = input("").strip()
        if not user_input:
            continue

        if user_input in exit_keywords:
            print("Baik, terima kasih telah menggunakan layanan Halovet. Semoga hewan peliharaan Anda sehat selalu!")
            return

        handled = handle_intent(user_input, on_complete=lambda: None)

if __name__ == "__main__":
    print("Halo. Terima kasih sudah menghubungi admin Halovet.")
    handle_menu()