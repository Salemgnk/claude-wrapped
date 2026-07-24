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
```

> **`--images`** capture chaque écran en PNG partageable (nécessite un Chrome/Chromium ;
> aucune dépendance Python ajoutée). **Exécutable uniquement en CLI** (données locales).

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
```

> **`--images`** captures each screen as a shareable PNG (needs Chrome/Chromium; no Python
> dependency added). **CLI-only** (local data). Then open the `.html` and scroll.

## Crédits / Credits

- Idée & moteur d'analyse / idea & parsing engine : **[@HKafuiEPI](https://github.com/HKafuiEPI)** — [My Claude Wrapped](https://github.com/HKafuiEPI/my_claude_wrapped)
- Direction artistique néo-brutaliste / neo-brutalist art direction : reprise de [Git Wrapped](https://github.com/Salemgnk/git-wrapped)
- Polices / fonts : Space Grotesk & Space Mono (OFL)
