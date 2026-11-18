#!/usr/bin/env python3
"""Crea le versioni citabili. Lo esegue GitHub Actions dopo ogni pubblicazione.

Per ogni ricerca pubblicata (non bozza) che ha nella scheda una riga
    versione: "1.0"
e per cui non esiste ancora l'etichetta (tag)  v1.0-nome-della-ricerca:

  1. costruisce il PDF della ricerca;
  2. calcola le impronte SHA-256 di PDF e sorgenti e le fa marcare da
     OpenTimestamps;
  3. registra tutto in un commit dedicato, lo etichetta e crea la Release
     su GitHub con PDF, impronte e marche allegati.

Zenodo, se collegato al repository, vede la Release, ne archivia il
contenuto (PDF compreso, perché sta nel commit etichettato) e assegna il DOI.

Per una versione successiva basta cambiare il numero: versione: "1.1".
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

RADICE = Path(__file__).resolve().parent.parent
RICERCHE = RADICE / "ricerche"
REPO = os.environ.get("GITHUB_REPOSITORY", "fabiocassinelli/dietroalmonte")
SITO = "https://dietroalmonte.it"
PROVA = "--prova" in sys.argv          # fa tutto tranne inviare a GitHub
IDENTITA = ["-c", "user.name=github-actions[bot]",
            "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com",
            "-c", "commit.gpgsign=false", "-c", "tag.gpgsign=false"]


def esegui(comando: list[str], controlla: bool = True, **opzioni) -> str:
    esito = subprocess.run(comando, cwd=RADICE, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", **opzioni)
    if controlla and esito.returncode != 0:
        sys.stderr.write(esito.stdout[-3000:] + "\n" + esito.stderr[-3000:] + "\n")
        raise SystemExit(f"comando fallito: {' '.join(comando)}")
    return esito.stdout.strip()


def riuscito(comando: list[str]) -> bool:
    return subprocess.run(comando, cwd=RADICE, capture_output=True).returncode == 0


def scheda(qmd: Path) -> dict:
    testo = qmd.read_text(encoding="utf-8")
    m = re.match(r"\A---\r?\n(.*?)\r?\n---[ \t]*\r?\n", testo, re.S)
    return (yaml.safe_load(m.group(1)) or {}) if m else {}


def impronta(file: Path) -> str:
    return hashlib.sha256(file.read_bytes()).hexdigest()


def da_rilasciare() -> list[dict]:
    trovate = []
    for cartella in sorted(RICERCHE.iterdir()):
        qmd = cartella / "index.qmd"
        if not cartella.is_dir() or cartella.name.startswith(("_", ".")) or not qmd.exists():
            continue
        dati = scheda(qmd)
        versione = str(dati.get("versione") or "").strip()
        if not versione or dati.get("draft") is True:
            continue
        if not re.fullmatch(r"\d+(\.\d+){0,2}", versione):
            print(f"::error::{cartella.name}: «versione: {versione}» non valida "
                  f"(usa solo numeri e punti, per esempio \"1.0\").")
            continue
        breve = re.sub(r"^\d{4}-\d{2}-", "", cartella.name)
        tag = f"v{versione}-{breve}"
        if riuscito(["git", "rev-parse", "--verify", "--quiet", f"refs/tags/{tag}"]):
            continue
        trovate.append({"cartella": cartella, "dati": dati, "versione": versione,
                        "breve": breve, "tag": tag})
    return trovate


def costruisci_pdf(r: dict, destinazione: Path) -> Path:
    qmd = r["cartella"] / "index.qmd"
    # riga in testa al PDF: versione, indirizzo, licenza (la inserisce
    # scripts/da-completare.lua leggendo la variabile DAM_TESTATA)
    indirizzo = f"{SITO}/ricerche/{r['cartella'].name}/"
    testata = (f"*Dietro al Monte* · versione {r['versione']} · <{indirizzo}> · "
               f"licenza CC BY-NC-SA 4.0")
    ambiente = dict(os.environ, DAM_PUBBLICA="1", DAM_TESTATA=testata)
    esegui(["quarto", "render", str(qmd.relative_to(RADICE)), "--to", "typst",
            "-M", "citeproc:true"], env=ambiente)
    prodotto = RADICE / "_site" / qmd.relative_to(RADICE).with_suffix(".pdf")
    if not prodotto.exists():
        raise SystemExit(f"non trovo il PDF atteso: {prodotto}")
    pdf = destinazione / f"{r['breve']}-v{r['versione']}.pdf"
    shutil.copyfile(prodotto, pdf)
    return pdf


def scrivi_impronte(r: dict, destinazione: Path, pdf: Path, commit: str) -> Path:
    righe = [f"# {r['dati'].get('title', r['breve'])} - versione {r['versione']}",
             f"# repository: https://github.com/{REPO}",
             f"# commit dei sorgenti: {commit}",
             "# formato di ogni riga: impronta SHA-256, due spazi, file",
             f"{impronta(pdf)}  {pdf.name}"]
    tracciati = esegui(["git", "ls-files", "-z", "--", str(r["cartella"].relative_to(RADICE)),
                        "fonti", "assets/csl"]).split("\0")
    for percorso in sorted(p for p in tracciati if p):
        righe.append(f"{impronta(RADICE / percorso)}  {percorso}")
    elenco = destinazione / "SHA256SUMS.txt"
    elenco.write_text("\n".join(righe) + "\n", encoding="utf-8", newline="\n")
    return elenco


def marca(file: Path) -> bool:
    ok = subprocess.run(["ots", "stamp", file.name], cwd=file.parent,
                        capture_output=True).returncode == 0
    return ok and Path(str(file) + ".ots").exists()


def metadati_zenodo(r: dict) -> dict:
    base = json.loads((RADICE / ".zenodo.json").read_text(encoding="utf-8"))
    d = r["dati"]
    titolo = str(d.get("title", r["breve"])).strip()
    sottotitolo = str(d.get("subtitle") or "").strip()
    riassunto = str(d.get("abstract") or d.get("description") or "").strip()
    indirizzo = f"{SITO}/ricerche/{r['cartella'].name}/"
    base["title"] = f"{titolo}. {sottotitolo}" if sottotitolo else titolo
    base["version"] = r["versione"]
    base["description"] = (
        f"<p>{riassunto}</p>"
        f"<p>Ricerca pubblicata su <em>Dietro al Monte</em>: "
        f"<a href=\"{indirizzo}\">{indirizzo}</a>. Questo deposito contiene il PDF della "
        f"versione {r['versione']} (cartella <code>rilasci/{r['tag']}/</code>) e i sorgenti "
        f"completi del sito alla stessa data.</p>")
    categorie = [str(c) for c in (d.get("categories") or [])]
    base["keywords"] = list(dict.fromkeys(categorie + list(base.get("keywords", []))))
    base["related_identifiers"] = [
        {"identifier": indirizzo, "relation": "isIdenticalTo", "scheme": "url"}]
    return base


def note_release(r: dict, pdf: Path, marcati: bool) -> str:
    titolo = r["dati"].get("title", r["breve"])
    indirizzo = f"{SITO}/ricerche/{r['cartella'].name}/"
    righe = [f"Versione citabile **{r['versione']}** di «{titolo}».", "",
             f"Pagina della ricerca: {indirizzo}", "", "Allegati:", "",
             f"- `{pdf.name}` — il testo in PDF",
             "- `SHA256SUMS.txt` — impronte SHA-256 del PDF e dei sorgenti"]
    if marcati:
        righe.append("- file `.ots` — marche temporali OpenTimestamps dei due file sopra")
    righe += ["", f"Come verificare autore e data: {SITO}/metodo.html"]
    return "\n".join(righe) + "\n"


def rilascia(r: dict, commit: str) -> None:
    tag = r["tag"]
    print(f"\n== {tag} ==")
    destinazione = RADICE / "rilasci" / tag
    destinazione.mkdir(parents=True, exist_ok=True)
    pdf = costruisci_pdf(r, destinazione)
    elenco = scrivi_impronte(r, destinazione, pdf, commit)
    marcati = marca(pdf) and marca(elenco)
    if not marcati:
        print("::warning::OpenTimestamps non ha risposto: Release senza file .ots "
              "(resta valida la marca automatica della pubblicazione).")
    zenodo_originale = (RADICE / ".zenodo.json").read_text(encoding="utf-8")
    (RADICE / ".zenodo.json").write_text(
        json.dumps(metadati_zenodo(r), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n")

    titolo_release = f"{r['dati'].get('title', r['breve'])} — versione {r['versione']}"
    note = RADICE / "_note-release.md"
    note.write_text(note_release(r, pdf, marcati), encoding="utf-8")
    try:
        esegui(["git", "checkout", "--quiet", "--detach", commit])
        esegui(["git", "add", "-f", str(destinazione.relative_to(RADICE)), ".zenodo.json"])
        esegui(["git", *IDENTITA, "commit", "--quiet", "-m",
                f"Versione {r['versione']} di «{r['dati'].get('title', r['breve'])}»"])
        esegui(["git", *IDENTITA, "tag", "-a", tag, "-m", titolo_release])
        allegati = sorted(str(p.relative_to(RADICE)) for p in destinazione.iterdir())
        if PROVA:
            print("Prova: commit ed etichetta creati in locale, niente invio a GitHub.")
            print("Allegati:", ", ".join(allegati))
        else:
            esegui(["git", "push", "--quiet", "origin", f"refs/tags/{tag}"])
            esegui(["gh", "release", "create", tag, *allegati, "--verify-tag",
                    "--title", titolo_release, "--notes-file", str(note)])
            print(f"Release creata: https://github.com/{REPO}/releases/tag/{tag}")
    finally:
        note.unlink(missing_ok=True)
        riuscito(["git", "checkout", "--quiet", "--detach", commit])
        (RADICE / ".zenodo.json").write_text(zenodo_originale, encoding="utf-8", newline="\n")
        if not PROVA:
            shutil.rmtree(RADICE / "rilasci", ignore_errors=True)


def main() -> int:
    elenco = da_rilasciare()
    if not elenco:
        print("Nessuna nuova versione da creare.")
        return 0
    commit = esegui(["git", "rev-parse", "HEAD"])
    for r in elenco:
        rilascia(r, commit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
