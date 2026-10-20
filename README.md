# Word Radar

A semantic word-guessing game (a "Cémantix"-style game) built to illustrate how word embeddings work.

Each team has **120 seconds**. A secret word is hidden; the team types words and the AI tells how close each one is to the secret word (by meaning, not by letters). Found it? A new secret word starts immediately and the clock keeps running.

- **Radar**: the secret word is the star ★ in the centre, every guess is a dot. The closer to the centre, the closer in meaning.
- **Zones**: Freezing, Cold, Warm, Hot, Burning.
- **Score per secret word (0 to 5)**: only the best zone reached counts, not the number of guesses. Freezing = 0, Cold = 1, Warm = 2, Hot = 3, Burning = 4, word found = 5. Scores add up over the 120 s. Scores are not saved anywhere: the coordinator writes them down.
- **Hint**: available after 30 s on a word (free).
- Typos are tolerated (one-letter mistakes on the secret word count as found if the typed word is not a real word for the model).
- Each secret word is given only once across all teams (shared list on the server), and two consecutive words never share the same theme.

## How it works

- `server.py`: FastAPI server + [fastText](https://fasttext.cc) English vectors (`cc.en.300.bin`). Similarity = cosine similarity between the typed word and the secret word, rescaled to 0-1.
- `index.html`: the game page (radar, timer, score), served by the server at `/`.
- The angle of a dot on the radar is decorative; only the distance to the centre is meaningful.

## Requirements

- Linux (tested on Ubuntu) with **Python 3.12** (fastText does not build on Python 3.14)
- About **12 GB free disk** and **8 GB free RAM** (the model is about 7 GB)
- `build-essential` (to compile fastText)

```bash
sudo apt install python3.12 python3.12-venv build-essential wget
```

## Setup

```bash
git clone https://github.com/DhiaYoussefIssatSo/Radar.git
cd Radar

python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
CFLAGS="-include cstdint" CXXFLAGS="-include cstdint" pip install -r requirements.txt
```

The model is **not in the repository** (too big). Download it once, inside the project folder:

```bash
wget -c https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.en.300.bin.gz
gunzip cc.en.300.bin.gz
ls -lh cc.en.300.bin     # about 7 GB
```

If the download stops, run the same `wget -c` line again: it resumes where it stopped.

## Run

```bash
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8000
```

Wait for `Application startup complete` (loading the model takes a minute or more), then open `http://localhost:8000`.

Shortcut: `./lancer.sh` does the same and opens the browser automatically (run `chmod +x lancer.sh` once).

### Playing on several computers

Run the server on **one** machine only. Find its IP with `hostname -I`, then on the other devices (same network) open `http://IP_OF_THE_SERVER:8000`. Each device plays its own game, and the server makes sure teams do not get the same secret words.

Before an event, open `http://localhost:8000/reset` to reset the list of words already given.

## Tests and tuning

With the server running, in another terminal:

```bash
python3 test.py            # 50 test guesses with expected closeness and resulting zone
curl "localhost:8000/check" > check.json   # 8 nearest neighbours of each secret word
```

- Secret words and hints: the `SECRETS` list in `server.py` (word, hint, theme).
- Zone thresholds: the line `s = min(1.0, max(0.0, (cos - 0.25) / 0.55))` in `guess()` and the matching values in `index.html` (`L` array and `pts` function).

## Troubleshooting

- **`fasttext-wheel` fails to build**: check you are on Python 3.12 (`python --version` inside the venv) and that `build-essential` is installed. Keep the `CFLAGS` / `CXXFLAGS` variables on the install command.
- **The server tries to download the model at startup**: `cc.en.300.bin` is not in the project folder. Download it with the `wget -c` command above.
- **`Address already in use`**: a server is already running on port 8000. Close its terminal or press `Ctrl+C` there.
- **Other devices cannot connect**: check both are on the same network, the IP from `hostname -I`, and that the network allows device-to-device traffic (some university Wi-Fi blocks it; use a phone hotspot or a cable).
- **Page looks outdated**: hard refresh with `Ctrl+Shift+R`.
