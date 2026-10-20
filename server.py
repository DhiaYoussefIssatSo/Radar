import random, threading, unicodedata
import numpy as np
import fasttext, fasttext.util
from fastapi import FastAPI
from fastapi.responses import FileResponse

fasttext.util.download_model('en', if_exists='ignore')
ft = fasttext.load_model('cc.en.300.bin')

# (word, hint, theme)
SECRETS = [
    ("beach", "Where the land stops and holidaymakers settle in", "water"),
    ("river", "It is born high up and always ends up lower down", "water"),
    ("forest", "A territory where wood is king, far from the roads", "nature"),
    ("mountain", "A stone giant that you climb out of breath", "nature"),
    ("desert", "Where rain is an absolute rarity", "nature"),
    ("storm", "The sky growls before it cries", "weather"),
    ("winter", "Days get shorter and the frost settles in", "time"),
    ("night", "It falls every evening and never misses the appointment", "time"),
    ("school", "You go in small and come out wiser", "place"),
    ("hospital", "A building where white dominates and the wait is long", "place"),
    ("airport", "A place where you wait to take off, suitcase in hand", "transport"),
    ("train", "It never strays from its path and whistles on arrival", "transport"),
    ("bicycle", "It moves thanks to your legs and never pollutes", "transport"),
    ("kitchen", "You hear sizzling there, and the smell reaches the living room", "home"),
    ("window", "A frame with no painting that shows the world", "home"),
    ("sofa", "It welcomes naps and evenings in front of the screen", "home"),
    ("bread", "Golden outside, soft inside, it leaves the oven before dawn", "food"),
    ("cheese", "It ferments slowly, and some kinds smell very strong", "food"),
    ("chocolate", "It melts in the mouth and comes from a bean", "food"),
    ("coffee", "A small black cup to start the day", "drink"),
    ("computer", "It calculates faster than any human", "tech"),
    ("phone", "It fits in your pocket and rings at the worst moment", "tech"),
    ("internet", "You get lost in it for hours without leaving home", "tech"),
    ("football", "Millions shout at a screen when a ball crosses a line", "sport"),
    ("music", "It passes through walls without being seen", "art"),
    ("guitar", "You strum it around a campfire", "art"),
    ("cat", "It sleeps sixteen hours a day and thinks it rules the house", "animal"),
    ("horse", "Its strength was long used as a unit to measure engines", "animal"),
]

def norm(w):
    w = unicodedata.normalize("NFD", w.lower().strip())
    return "".join(c for c in w if unicodedata.category(c) != "Mn")

def vec(w):
    v = ft.get_word_vector(w)
    return v / (np.linalg.norm(v) + 1e-9)

def edit1(a, b):
    """True si a et b different d'au plus une lettre (substitution, ajout ou oubli)."""
    if a == b:
        return True
    if abs(len(a) - len(b)) > 1:
        return False
    if len(a) > len(b):
        a, b = b, a
    i = 0
    while i < len(a) and a[i] == b[i]:
        i += 1
    return a[i+1:] == b[i+1:] or a[i:] == b[i+1:]

rng = np.random.default_rng(42)
U1, U2 = rng.normal(size=300), rng.normal(size=300)

LOCK = threading.Lock()
USED = set()          # words already given (all teams)

app = FastAPI()

@app.get("/")
def index():
    return FileResponse("index.html")

@app.get("/new")
def new(prev: int = -1):
    with LOCK:
        pc = SECRETS[prev][2] if 0 <= prev < len(SECRETS) else None
        free = [i for i in range(len(SECRETS)) if i not in USED and SECRETS[i][2] != pc]
        if not free:
            USED.clear()
            free = [i for i in range(len(SECRETS)) if SECRETS[i][2] != pc]
        i = random.choice(free)
        USED.add(i)
    return {"id": i, "hint": SECRETS[i][1]}

@app.get("/reset")
def reset():
    with LOCK:
        USED.clear()
    return {"ok": True}

@app.get("/guess")
def guess(id: int, w: str):
    secret = SECRETS[id][0]
    w1, s1 = norm(w), norm(secret)
    typo = edit1(w1, s1) and ft.get_word_id(w.lower().strip()) < 0
    if w1 in (s1, s1 + "s", s1 + "es") or typo:
        return {"found": True, "s": 1.0, "a": 0, "name": secret.upper()}
    vs, vw = vec(secret), vec(w.lower().strip())
    cos = float(vs @ vw)
    s = min(1.0, max(0.0, (cos - 0.25) / 0.55))   # to calibrate
    r = vw - (vw @ vs) * vs
    a = float(np.degrees(np.arctan2(r @ U2, r @ U1)))
    return {"found": False, "s": round(s, 3), "a": round(a, 1), "cos": round(cos, 3)}

@app.get("/reveal")
def reveal(id: int):
    return {"name": SECRETS[id][0].upper()}

@app.get("/check")
def check():
    words = [{"word": w, "neighbors": [[round(s, 2), n] for s, n in ft.get_nearest_neighbors(w, 8)]}
             for w, _, _ in SECRETS]
    V = np.array([vec(w) for w, _, _ in SECRETS])
    M = V @ V.T
    pairs = [[SECRETS[i][0], SECRETS[j][0], round(float(M[i, j]), 2)]
             for i in range(len(SECRETS)) for j in range(i + 1, len(SECRETS)) if M[i, j] > 0.5]
    return {"pairs_too_close": pairs, "words": words}