import signal
import threading


def main():
    stop = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    print("extract worker started")
    while not stop.wait(60):
        print("extract worker alive")


if __name__ == "__main__":
    main()
