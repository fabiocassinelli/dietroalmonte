#!/usr/bin/env python3
"""Marca temporale automatica (OpenTimestamps). Lo esegue GitHub Actions.

A ogni pubblicazione:
  1. scrive un elenco con l'impronta SHA-256 di ogni file del repository
     (così com'è nel commit appena pubblicato);
  2. fa marcare l'elenco da OpenTimestamps (file .ots);
  3. salva elenco e marca nel ramo `marche-temporali`, cartella dell'anno.

Con --solo-completa non crea nulla: completa le marche ancora «in attesa»
(servono alcune ore perché la blockchain di Bitcoin le registri).

Il ramo principale non viene mai toccato: sul tuo computer non cambia nulla.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

RAMO = "marche-temporali"
RADICE = Path(__file__).resolve().parent.parent
REPO = os.environ.get("GITHUB_REPOSITORY", "fabiocassinelli/dietroalmonte")
QUANTE_DA_COMPLETARE = 80

LEGGIMI = f"""# Marche temporali di «Dietro al Monte»

Questo ramo è scritto in automatico. Per ogni pubblicazione del sito contiene:

- un file `.sha256`: l'elenco delle impronte SHA-256 di tutti i file del
  repository in quel momento (in testa c'è il commit a cui si riferisce);
- un file `.sha256.ots`: la marca temporale OpenTimestamps di quell'elenco.

Come verificare: https://dietroalmonte.it/metodo.html

Repository: https://github.com/{REPO}
"""


def esegui(comando: list[str], cwd: Path | None = None, controlla: bool = True,
           binario: bool = False):
    esito = subprocess.run(comando, cwd=cwd or RADICE, capture_output=True)
    if controlla and esito.returncode != 0:
        sys.stderr.write(esito.stderr.decode("utf-8", "replace"))
        raise SystemExit(f"comando fallito: {' '.join(comando)}")
    if binario:
        return esito.stdout
    return esito.stdout.decode("utf-8", "replace").strip()


def riuscito(comando: list[str], cwd: Path | None = None) -> bool:
    return subprocess.run(comando, cwd=cwd or RADICE, capture_output=True).returncode == 0


def prepara_ramo(lavoro: Path) -> None:
    """Mette in `lavoro` una copia del ramo delle marche (creandolo se manca)."""
    riuscito(["git", "fetch", "--quiet", "origin", f"+refs/heads/{RAMO}:refs/remotes/origin/{RAMO}"])
    if riuscito(["git", "rev-parse", "--verify", "--quiet", f"refs/remotes/origin/{RAMO}"]):
        esegui(["git", "worktree", "add", "--quiet", "-B", RAMO, str(lavoro), f"origin/{RAMO}"])
    else:
        esegui(["git", "worktree", "add", "--quiet", "--detach", str(lavoro)])
        esegui(["git", "checkout", "--quiet", "--orphan", RAMO], cwd=lavoro)
        esegui(["git", "rm", "-rf", "--quiet", "."], cwd=lavoro, controlla=False)
        for avanzo in lavoro.iterdir():
            if avanzo.name != ".git" and avanzo.is_file():
                avanzo.unlink()
    (lavoro / "LEGGIMI.md").write_text(LEGGIMI, encoding="utf-8", newline="\n")


def elenco_impronte(commit: str, quando: dt.datetime) -> str:
    righe = [
        "# Dietro al Monte - impronte SHA-256 dei file del repository",
        f"# repository: https://github.com/{REPO}",
        f"# commit: {commit}",
        f"# creato (UTC): {quando:%Y-%m-%d %H:%M:%S}",
        "# formato di ogni riga: impronta, due spazi, percorso del file",
    ]
    percorsi = esegui(["git", "ls-tree", "-r", "-z", "--name-only", commit],
                      binario=True).decode("utf-8").split("\0")
    for percorso in sorted(p for p in percorsi if p):
        contenuto = esegui(["git", "cat-file", "blob", f"{commit}:{percorso}"], binario=True)
        righe.append(f"{hashlib.sha256(contenuto).hexdigest()}  {percorso}")
    return "\n".join(righe) + "\n"


def marca(file: Path) -> bool:
    for tentativo in range(3):
        if riuscito(["ots", "stamp", str(file)], cwd=file.parent) and \
                Path(str(file) + ".ots").exists():
            return True
        time.sleep(20 * (tentativo + 1))
    return False


def completa(lavoro: Path) -> int:
    """Prova a completare le marche ancora in attesa. Restituisce quante."""
    completate = 0
    marche = sorted(lavoro.rglob("*.ots"))[-QUANTE_DA_COMPLETARE:]
    for m in marche:
        info = subprocess.run(["ots", "info", str(m)], capture_output=True, text=True).stdout
        if "BitcoinBlockHeaderAttestation" in info:
            continue
        subprocess.run(["ots", "upgrade", str(m)], capture_output=True)
        copia = Path(str(m) + ".bak")
        if copia.exists():
            copia.unlink()
            completate += 1
    return completate


def pubblica(lavoro: Path, messaggio: str) -> None:
    esegui(["git", "add", "-A"], cwd=lavoro)
    if riuscito(["git", "diff", "--cached", "--quiet"], cwd=lavoro):
        print("Nessuna novità da salvare nel ramo delle marche.")
        return
    identita = ["-c", "user.name=github-actions[bot]",
                "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com",
                "-c", "commit.gpgsign=false"]
    esegui(["git", *identita, "commit", "--quiet", "-m", messaggio], cwd=lavoro)
    if "--senza-invio" in sys.argv:
        print("Prova: salvato nel ramo locale, non inviato.")
        return
    for _ in range(3):
        if riuscito(["git", "push", "--quiet", "origin", f"HEAD:refs/heads/{RAMO}"], cwd=lavoro):
            print(f"Salvato nel ramo {RAMO}.")
            return
        riuscito(["git", *identita, "pull", "--quiet", "--rebase", "origin", RAMO], cwd=lavoro)
    raise SystemExit("non sono riuscito a inviare il ramo delle marche.")


def main() -> int:
    solo_completa = "--solo-completa" in sys.argv
    commit = esegui(["git", "rev-parse", "HEAD"])
    quando = dt.datetime.now(dt.timezone.utc)
    esito = 0
    with tempfile.TemporaryDirectory(prefix="dam-marche-") as tmp:
        lavoro = Path(tmp) / "ramo"
        prepara_ramo(lavoro)
        try:
            messaggio = "Completo le marche temporali in attesa"
            if not solo_completa:
                gia = list(lavoro.rglob(f"*_{commit[:12]}.sha256"))
                if gia:
                    print(f"Il commit {commit[:12]} ha già la sua marca: {gia[0].name}")
                else:
                    anno = lavoro / f"{quando:%Y}"
                    anno.mkdir(exist_ok=True)
                    elenco = anno / f"{quando:%Y-%m-%dT%H%M%SZ}_{commit[:12]}.sha256"
                    elenco.write_text(elenco_impronte(commit, quando), encoding="utf-8",
                                      newline="\n")
                    if marca(elenco):
                        print(f"Marca temporale creata: {elenco.name}.ots")
                        messaggio = f"Marca temporale del commit {commit[:12]}"
                    else:
                        elenco.unlink()
                        print("::error::OpenTimestamps non ha risposto: questa pubblicazione "
                              "non ha la marca. Riprova da Actions → «Pubblica il sito» → "
                              "Run workflow.")
                        esito = 1
            n = completa(lavoro)
            if n:
                print(f"Marche completate (registrate nella blockchain): {n}")
            pubblica(lavoro, messaggio)
        finally:
            riuscito(["git", "worktree", "remove", "--force", str(lavoro)])
    return esito


if __name__ == "__main__":
    sys.exit(main())
