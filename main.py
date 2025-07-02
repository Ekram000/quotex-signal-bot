from web_dashboard import start_dashboard
from quotex_bot import start_bot

if __name__ == "__main__":
    import threading
    threading.Thread(target=start_dashboard).start()
    start_bot()