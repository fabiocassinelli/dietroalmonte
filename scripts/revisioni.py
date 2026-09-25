#!/usr/bin/env python3
"""
Genera la cronologia delle revisioni di ogni ricerca leggendo il git log.

Eseguito automaticamente da Quarto prima di ogni render (chiave
`pre-render` in _quarto.yml). Per ogni cartella in ricerche/ scrive un
file `_revisioni.md` che l'articolo include con:

    {{< include _revisioni.md >}}

I file generati iniziano con un underscore, quindi Quarto non li
pubblica come pagine a sé. Sono in .gitignore: si rigenerano sempre.

Se il repository non ha ancora storia (primo clone, primo commit), il
file viene comunque creato vuoto, così l'include non fallisce.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

RICERCHE = Path("ricerche")
MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
        "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]


def git(*args: str) -> str:
    try:
        return subprocess.run(
            ["git", *args], capture_output=True, text=True, check=True
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def data_estesa(iso: str) -> str:
    """2026-03-14 -> 14 marzo 2026"""
    try:
        anno, mese, giorno = iso.split("-")
        return f"{int(giorno)} {MESI[int(mese) - 1]} {anno}"
    except (ValueError, IndexError):
        return iso


def tag_della_cartella(cartella: Path) -> list[tuple[str, str]]:
    """Tag che toccano questa ricerca, con la loro data. Dal più recente."""
    righe = git("tag", "--list", f"*{cartella.name.split('-', 2)[-1]}*",
                "--format=%(refname:short)%09%(creatordate:short)")
    out = []
    for riga in righe.splitlines():
        if "\t" in riga:
            tag, data = riga.split("\t", 1)
            out.append((tag.strip(), data.strip()))
    return sorted(out, key=lambda t: t[1], reverse=True)


def commit_della_cartella(cartella: Path, limite: int = 12):
    righe = git("log", f"-{limite}", "--date=short",
                "--format=%h%09%ad%09%s", "--", str(cartella))
    out = []
    for riga in righe.splitlines():
        parti = riga.split("\t")
        if len(parti) == 3:
            out.append(tuple(p.strip() for p in parti))
    return out


def scrivi(cartella: Path) -> None:
    destinazione = cartella / "_revisioni.md"
    tag = tag_della_cartella(cartella)
    commit = commit_della_cartella(cartella)

    if not commit:
        destinazione.write_text("", encoding="utf-8")
        return

    righe = [
        "",
        "## Cronologia delle revisioni {.appendix}",
        "",
    ]

    if tag:
        for nome, data in tag:
            versione = nome.split("-", 1)[0].lstrip("v")
            righe.append(f"**Versione {versione}** — {data_estesa(data)}  ")
        righe.append("")

    prima = commit[-1]
    righe.append(
        f"Prima stesura registrata il {data_estesa(prima[1])}. "
        f"Ultima modifica il {data_estesa(commit[0][1])}. "
        f"{len(commit)} interventi registrati."
    )
    righe.append("")

    righe.append('::: {.callout-note collapse="true" appearance="simple"}')
    righe.append("## Tutte le modifiche")
    righe.append("")
    righe.append("| Data | Modifica | Commit |")
    righe.append("|---|---|---|")
    for sha, data, messaggio in commit:
        messaggio = messaggio.replace("|", "\\|")
        righe.append(f"| {data_estesa(data)} | {messaggio} | `{sha}` |")
    righe.append("")
    righe.append(
        "Ogni commit è firmato crittograficamente. Vedi il "
        "[metodo](../../metodo.qmd) per verificarli."
    )
    righe.append(":::")
    righe.append("")

    destinazione.write_text("\n".join(righe), encoding="utf-8")


def main() -> None:
    if not RICERCHE.is_dir():
        return
    for cartella in sorted(RICERCHE.iterdir()):
        if cartella.is_dir() and (cartella / "index.qmd").exists():
            scrivi(cartella)
            print(f"revisioni: {cartella.name}")


if __name__ == "__main__":
    main()
