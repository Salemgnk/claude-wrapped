<div align="center">

# ◆ Claude Wrapped — Neo-Brutalist Edition

**Ton année [Claude Code](https://claude.com/claude-code), wrappée en néo-brutalisme.**
**Your Claude Code year, wrapped — neo-brutalist style.**

Lit tes transcripts Claude Code **en local** et génère une page HTML unique,
partageable et autonome — blocs à ombre dure, accents francs, polices mono, dans
l'esprit de [Git Wrapped](https://github.com/Salemgnk/git-wrapped).

`🇫🇷 Français` · `🇬🇧 English` · MIT

</div>

---

> **Adaptation néo-brutaliste** de **[My Claude Wrapped — Arcade Edition](https://github.com/HKafuiEPI/my_claude_wrapped)**
> par **[@HKafuiEPI](https://github.com/HKafuiEPI)** (👏 tout le crédit de l'idée et de l'analyse des
> transcripts lui revient). Ici on garde son moteur, on change la peau : direction artistique
> néo-brutaliste au lieu de l'arcade rétro. / Neo-brutalist re-skin of **@HKafuiEPI**'s
> *My Claude Wrapped*; same engine, different art direction.

## 🇫🇷 Français

### C'est quoi ?

Un générateur qui transforme ton historique **local** Claude Code
(`~/.claude/projects/**/*.jsonl`) en une page « Wrapped » à la Spotify, look
**néo-brutaliste**. Aucune donnée n'est envoyée nulle part : tout tourne en local
et la page ne contient **que des chiffres agrégés** (jamais le contenu des conversations).

### Installation & utilisation

Aucune dépendance — juste **Python 3.8+**.

```bash
git clone git@github.com:Salemgnk/claude-wrapped.git
cd claude-wrapped
python3 generate.py                 # FR  -> claude_wrapped.html
python3 generate.py --lang en       # EN  -> claude_wrapped.en.html
python3 generate.py --days 30       # 30 derniers jours
python3 generate.py --images        # exporte 1 PNG par écran -> images/
python3 generate.py --video         # vidéo diaporama (fondus) -> claude_wrapped.mp4
python3 generate.py --video --video-music song.mp3   # + musique
```

> **`--images`** capture chaque écran en PNG partageable ; **`--video`** les assemble en
> **mp4** (fondus enchaînés, ~3 s/écran, musique optionnelle). Nécessite **Chrome/Chromium**
> (et **ffmpeg** pour `--video`) ; aucune dépendance Python ajoutée, ignoré proprement si absent.
> **Exécutable uniquement en CLI** (données locales).

Puis ouvre le `.html` — navigation `←` `→`, `Espace`, clic ou swipe.

## 🇬🇧 English

### What is it?

A generator that turns your **local** Claude Code history
(`~/.claude/projects/**/*.jsonl`) into a Spotify-Wrapped-style page, **neo-brutalist**
look. Nothing is sent anywhere: everything runs locally and the page contains
**only aggregate numbers** (never conversation content).

### Install & usage

No dependencies — just **Python 3.8+**.

```bash
git clone git@github.com:Salemgnk/claude-wrapped.git
cd claude-wrapped
python3 generate.py                 # FR  -> claude_wrapped.html
python3 generate.py --lang en       # EN  -> claude_wrapped.en.html
python3 generate.py --images        # export one PNG per screen -> images/
python3 generate.py --video         # slideshow video (fades) -> claude_wrapped.mp4
python3 generate.py --video --video-music song.mp3   # + music
```

> **`--images`** captures each screen as a shareable PNG; **`--video`** stitches them into an
> **mp4** (crossfades, ~3s/screen, optional music). Needs **Chrome/Chromium** (and **ffmpeg**
> for `--video`); no Python dependency added, skipped gracefully if missing. **CLI-only** (local
> data). Then open the `.html` and scroll.

## Crédits / Credits

- Idée & moteur d'analyse / idea & parsing engine : **[@HKafuiEPI](https://github.com/HKafuiEPI)** — [My Claude Wrapped](https://github.com/HKafuiEPI/my_claude_wrapped)
- Direction artistique néo-brutaliste / neo-brutalist art direction : reprise de [Git Wrapped](https://github.com/Salemgnk/git-wrapped)
- Polices / fonts : Space Grotesk & Space Mono (OFL)
