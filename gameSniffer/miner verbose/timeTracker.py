import time

class Timer:
    def __init__(self, label):
        self.label = label
    def __enter__(self):
        self.start = time.time()
    def __exit__(self, exc_type, exc_value, traceback):
        elapsed = time.time() - self.start
        print(f"Temps total de {self.label} : {elapsed:.2f}s")