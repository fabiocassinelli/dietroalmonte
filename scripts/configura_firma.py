#!/usr/bin/env python3
"""Configura la firma delle modifiche (commit) con una chiave SSH.

Va eseguito UNA volta sola, sul computer da cui scrivi: doppio clic su
«Configura firma.bat». Che cosa fa:

  1. crea una chiave dedicata in  <cartella utente>/.ssh/dietroalmonte_firma
     (se esiste già la riusa);
  2. dice a Git, SOLO per questo progetto, di firmare ogni commit con
     quella chiave: da quel momento anche i commit fatti dal pannello
     «Source Control» di VS Code sono firmati, senza fare nulla;
  3. copia la chiave pubblica negli appunti e apre la pagina di GitHub
     dove incollarla.

La chiave non ha password, altrimenti VS Code non riuscirebbe a firmare
da solo: la protegge l'accesso al tuo utente di Windows.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

from comune import RADICE, attendi_invio, console_utf8, esci

CHIAVE = Path.home() / ".ssh" / "dietroalmonte_firma"
FIRMATARI = Path.home() / ".ssh" / "dietroalmonte_firmatari"
PAGINA = "https://github.com/settings/ssh/new"


def git(*argomenti: str, controlla: bool = True) -> str:
    esito = subprocess.run(["git", *argomenti], cwd=RADICE, capture_output=True,
                           text=True, encoding="utf-8", errors="replace")
    if controlla and esito.returncode != 0:
        esci(f"git {' '.join(argomenti)}\n{esito.stderr.strip()}")
    return esito.stdout.strip()


def trova_ssh_keygen() -> str:
    trovato = shutil.which("ssh-keygen")
    if trovato:
        return trovato
    # Git for Windows ne porta uno con sé, in Git\usr\bin
    posto_git = shutil.which("git")
    if posto_git:
        for su in Path(posto_git).resolve().parents:
            candidato = su / "usr" / "bin" / "ssh-keygen.exe"
            if candidato.exists():
                return str(candidato)
    esci("non trovo il programma ssh-keygen. Reinstalla Git for Windows "
         "(https://git-scm.com/download/win) con le opzioni predefinite.")
    return ""


def main() -> None:
    console_utf8()
    if not shutil.which("git"):
        esci("non trovo Git. Installa Git for Windows e riprova.")
    if not (RADICE / ".git").exists():
        esci("questa cartella non è ancora un repository Git: apri in VS Code la "
             "cartella del progetto collegata a GitHub e riprova da lì.")

    nome = git("config", "user.name", controlla=False)
    email = git("config", "user.email", controlla=False)
    if not nome:
        nome = input("Il tuo nome e cognome (comparirà nelle modifiche): ").strip()
        git("config", "--global", "user.name", nome)
    if not email:
        email = input("La tua e-mail, la stessa del tuo account GitHub: ").strip()
        git("config", "--global", "user.email", email)
    if not nome or not email:
        esci("servono nome ed e-mail.")

    pubblica = CHIAVE.with_name(CHIAVE.name + ".pub")
    if CHIAVE.exists() and pubblica.exists():
        print(f"Uso la chiave che esiste già: {CHIAVE}")
    else:
        CHIAVE.parent.mkdir(parents=True, exist_ok=True)
        esito = subprocess.run([trova_ssh_keygen(), "-q", "-t", "ed25519", "-N", "",
                                "-C", f"Dietro al Monte - firma di {email}",
                                "-f", str(CHIAVE)], capture_output=True, text=True)
        if esito.returncode != 0:
            esci("non sono riuscito a creare la chiave:\n" + esito.stderr.strip())
        print(f"Chiave creata: {CHIAVE}")

    testo_pubblica = pubblica.read_text(encoding="utf-8").strip()
    tipo_e_chiave = " ".join(testo_pubblica.split()[:2])
    FIRMATARI.write_text(f'{email} namespaces="git" {tipo_e_chiave}\n', encoding="utf-8")

    git("config", "--local", "gpg.format", "ssh")
    git("config", "--local", "user.signingkey", pubblica.as_posix())
    git("config", "--local", "commit.gpgsign", "true")
    git("config", "--local", "tag.gpgsign", "true")
    git("config", "--local", "gpg.ssh.allowedSignersFile", FIRMATARI.as_posix())
    print("Git ora firma ogni modifica di questo progetto (anche da VS Code).")

    copiata = False
    if sys.platform == "win32":
        try:
            subprocess.run("clip", input=testo_pubblica, text=True, shell=True, check=True)
            copiata = True
        except (OSError, subprocess.CalledProcessError):
            pass

    print("\nULTIMO PASSO, A MANO, SU GITHUB")
    print("-------------------------------")
    print(f"1. Si apre la pagina {PAGINA}")
    print("2. Title:    Dietro al Monte - firma")
    print("3. Key type: Signing Key      <-- importante: NON «Authentication Key»")
    print("4. Key:      incolla (Ctrl+V)" if copiata else "4. Key:      copia e incolla la riga qui sotto")
    print("5. Premi «Add SSH key».")
    print("\nLa chiave pubblica" + (" (già copiata negli appunti):" if copiata else ":"))
    print("\n" + testo_pubblica + "\n")
    print(f"L'e-mail delle modifiche è {email}: deve essere una delle e-mail")
    print("verificate del tuo account GitHub, altrimenti l'etichetta «Verified» non compare.")
    print("\nFai una copia di sicurezza dei due file della chiave su una chiavetta:")
    print(f"  {CHIAVE}\n  {pubblica}")
    if "--non-aprire" not in sys.argv:
        try:
            webbrowser.open(PAGINA)
        except Exception:
            pass


if __name__ == "__main__":
    try:
        main()
    finally:
        attendi_invio()
