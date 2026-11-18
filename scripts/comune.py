"""Funzioni condivise dagli script di Dietro al Monte (solo libreria standard)."""

from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
RICERCHE = RADICE / "ricerche"
MODELLI = RADICE / "_modelli"
SEGNO_CODA = "<!-- CODA"
RIGA_CODA = "<!-- CODA — da qui in giù la conversione da Word non tocca nulla -->"
CODA_STANDARD = (
    RIGA_CODA
    + "\n\n## Fonti archivistiche e bibliografia\n\n::: {#refs}\n:::\n\n"
    + "{{< include _revisioni.md >}}\n"
)


def console_utf8() -> None:
    """Fa scrivere correttamente le lettere accentate anche su Windows."""
    for flusso in (sys.stdout, sys.stderr):
        try:
            flusso.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def esci(messaggio: str, codice: int = 1) -> None:
    print()
    print("ERRORE: " + messaggio)
    sys.exit(codice)


def impronta(testo_o_byte) -> str:
    if isinstance(testo_o_byte, str):
        testo_o_byte = testo_o_byte.encode("utf-8")
    return hashlib.sha256(testo_o_byte).hexdigest()


def impronta_file(percorso: Path) -> str:
    h = hashlib.sha256()
    with open(percorso, "rb") as f:
        for blocco in iter(lambda: f.read(1 << 20), b""):
            h.update(blocco)
    return h.hexdigest()


def leggi(percorso: Path) -> str:
    return percorso.read_text(encoding="utf-8").replace("\r\n", "\n")


def scrivi(percorso: Path, testo: str) -> None:
    with open(percorso, "w", encoding="utf-8", newline="\n") as f:
        f.write(testo)


def dividi_qmd(testo: str) -> tuple[str, str, str]:
    """Divide un .qmd in (scheda, corpo, coda).

    scheda: dal primo '---' al secondo compreso (la scheda in alto);
    corpo:  il testo della ricerca;
    coda:   dalla riga '<!-- CODA' alla fine ('' se la riga non c'è).
    """
    scheda = ""
    resto = testo
    m = re.match(r"\A---\n.*?\n---[ \t]*\n", testo, re.S)
    if m:
        scheda = m.group(0)
        resto = testo[m.end():]
    coda = ""
    posizione = resto.find(SEGNO_CODA)
    if posizione >= 0:
        coda = resto[posizione:]
        resto = resto[:posizione]
    return scheda, resto, coda


def normalizza(corpo: str) -> str:
    """Forma del corpo usata per capire se è stato modificato a mano."""
    righe = [r.rstrip() for r in corpo.strip().split("\n")]
    return "\n".join(righe)


def valore_scheda(scheda: str, chiave: str) -> str | None:
    """Legge un valore semplice (su una riga) dalla scheda. None se manca."""
    m = re.search(rf"^{re.escape(chiave)}:[ \t]*(.*)$", scheda, re.M)
    if not m:
        return None
    v = m.group(1).split(" #")[0].strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
    return v


def e_bozza(scheda: str) -> bool:
    return (valore_scheda(scheda, "draft") or "").lower() == "true"


def cartelle_ricerche() -> list[Path]:
    if not RICERCHE.is_dir():
        return []
    return sorted(c for c in RICERCHE.iterdir()
                  if c.is_dir() and not c.name.startswith(("_", ".")))


def trova_quarto() -> str:
    q = shutil.which("quarto")
    if not q:
        esci("non trovo Quarto. Installa Quarto da https://quarto.org/docs/download/ "
             "e riapri VS Code.")
    return q


def esegui(comando: list[str], **opzioni) -> subprocess.CompletedProcess:
    return subprocess.run(comando, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", **opzioni)


def attendi_invio() -> None:
    """Se lo script è stato lanciato con doppio clic, tiene aperta la finestra."""
    if "--pausa" in sys.argv:
        try:
            input("\nPremi Invio per chiudere questa finestra...")
        except EOFError:
            pass
