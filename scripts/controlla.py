#!/usr/bin/env python3
"""Controlla che cosa manca prima di pubblicare.

Sul computer elenca i promemoria (non modifica nulla, tranne creare i file
`_revisioni.md` mancanti). Su GitHub Actions (`--ci`) blocca la
pubblicazione solo per gli errori veri.

Uso: doppio clic su «Controlla prima di pubblicare.bat», oppure in VS Code
Terminale → Esegui attività → «Controlla che cosa manca».
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from comune import (RADICE, attendi_invio, cartelle_ricerche, console_utf8, dividi_qmd,
                    e_bozza, impronta_file, leggi, valore_scheda)

ORCID_FINTO = "0009-0009-4455-0112"
CI = "--ci" in sys.argv


def pagine() -> list[Path]:
    trovate = []
    for p in sorted(RADICE.rglob("*.qmd")):
        parti = p.relative_to(RADICE).parts
        if any(x.startswith(("_", ".")) for x in parti):
            continue
        trovate.append(p)
    return trovate


def chiavi_fonti() -> tuple[set[str], list[str]]:
    chiavi: set[str] = set()
    errori: list[str] = []
    fonti = RADICE / "fonti" / "fonti.json"
    try:
        for voce in json.loads(fonti.read_text(encoding="utf-8")):
            if isinstance(voce, dict) and "id" in voce:
                chiavi.add(str(voce["id"]))
    except (OSError, ValueError) as e:
        errori.append(f"fonti/fonti.json non si riesce a leggere ({e}). "
                      f"Riesportalo da Zotero in formato CSL JSON.")
    bib = RADICE / "fonti" / "bibliografia.bib"
    if bib.exists():
        chiavi.update(re.findall(r"^@\w+\{\s*([^,\s]+)\s*,", leggi(bib), re.M))
    return chiavi, errori


def senza_codice(testo: str) -> str:
    """Toglie blocchi di codice, esempi e commenti: lì dentro le citazioni
    e i segnaposto sono solo esempi."""
    testo = re.sub(r"<!--.*?-->", "", testo, flags=re.S)
    testo = re.sub(r"^(`{3,}|~{3,}).*?^\1[ \t]*$", "", testo, flags=re.S | re.M)
    testo = re.sub(r"`[^`\n]*`", "", testo)
    return testo


def senza_riquadri(testo: str) -> str:
    """Toglie i riquadri DA COMPLETARE (che sul sito pubblico non compaiono)."""
    righe, dentro, livello = [], False, 0
    for riga in testo.split("\n"):
        m = re.match(r"^(:{3,})\s*(\{.*\})?\s*$", riga)
        if not dentro and m and m.group(2) and ".da-completare" in m.group(2):
            dentro, livello = True, len(m.group(1))
            continue
        if dentro:
            if m and not m.group(2) and len(m.group(1)) == livello:
                dentro = False
            continue
        righe.append(riga)
    return "\n".join(righe)


def main() -> int:
    console_utf8()
    errori: list[str] = []
    promemoria: list[str] = []
    chiavi, e = chiavi_fonti()
    errori += e

    for cartella in cartelle_ricerche():
        if (cartella / "index.qmd").exists() and not (cartella / "_revisioni.md").exists():
            (cartella / "_revisioni.md").write_text("", encoding="utf-8")
            promemoria.append(f"{cartella.name}: mancava _revisioni.md, l'ho creato vuoto.")
        bozza = cartella / "bozza.docx"
        stato = cartella / ".bozza.json"
        if bozza.exists() and not CI:
            try:
                fatta = json.loads(stato.read_text(encoding="utf-8")).get("bozza_sha256")
            except (OSError, ValueError):
                fatta = None
            if fatta is None:
                promemoria.append(f"{cartella.name}: bozza.docx non è mai stata convertita "
                                  f"(va bene se è ancora il modello vuoto).")
            elif fatta != impronta_file(bozza):
                promemoria.append(f"{cartella.name}: bozza.docx è cambiata dopo l'ultima "
                                  f"conversione. Riconvertila se vuoi pubblicare il testo nuovo.")

    for pagina in pagine():
        nome = pagina.relative_to(RADICE).as_posix()
        testo = leggi(pagina)
        scheda, corpo, coda = dividi_qmd(testo)
        bozza = e_bozza(scheda)
        etichetta = " (bozza: non viene pubblicata)" if bozza else ""
        pulito = senza_codice(corpo + coda)

        riquadri = len(re.findall(r"^:{3,}\s*\{[^}]*\.da-completare", pulito, re.M))
        if riquadri:
            promemoria.append(f"{nome}: {riquadri} "
                              f"{'riquadro' if riquadri == 1 else 'riquadri'} DA COMPLETARE{etichetta}.")
        pubblico = senza_riquadri(pulito)
        if "DA COMPLETARE" in scheda or "DA COMPLETARE" in pubblico:
            messaggio = (f"{nome}: la scritta DA COMPLETARE compare nella scheda o nel "
                         f"testo, fuori dai riquadri{etichetta}.")
            (promemoria if bozza else errori).append(messaggio)
        segnaposto = [x for x in ("SOTTOTITOLO:", "SIGLA_FONDO_UNITA", "AAAA mese GG")
                      if x in scheda or x in pubblico]
        if valore_scheda(scheda, "title") == "TITOLO":
            segnaposto.insert(0, "TITOLO")
        if segnaposto:
            messaggio = (f"{nome}: ci sono ancora i segnaposto del modello "
                         f"({', '.join(segnaposto)}){etichetta}.")
            (promemoria if bozza else errori).append(messaggio)

        citate = set(re.findall(r"(?<![\w.\\])@([A-Za-z0-9_][\w:.#$%&+?<>~/-]*[\w/]|[A-Za-z0-9_])",
                                pubblico))
        mancanti = sorted(c for c in citate if c not in chiavi)
        if mancanti:
            messaggio = (f"{nome}: citazioni senza voce in fonti/fonti.json o "
                         f"bibliografia.bib: {', '.join('@' + c for c in mancanti)}{etichetta}.")
            (promemoria if bozza else errori).append(messaggio)

        if "ricerche" in pagina.relative_to(RADICE).parts[:1] and pagina.name == "index.qmd" \
                and pagina.parent != RADICE / "ricerche":
            if "_revisioni.md" not in coda and "_revisioni.md" not in corpo:
                promemoria.append(f"{nome}: manca in fondo la riga "
                                  "{{< include _revisioni.md >}} (niente cronologia).")
            versione = valore_scheda(scheda, "versione")
            if versione and bozza:
                promemoria.append(f"{nome}: ha «versione: {versione}» ma è ancora bozza: "
                                  f"la versione citabile non verrà creata finché resta draft: true.")
            if versione and not re.fullmatch(r"\d+(\.\d+){0,2}", versione):
                errori.append(f"{nome}: «versione: {versione}» non va bene. "
                              f"Usa solo numeri e punti, per esempio \"1.0\".")

    tutto = ""
    for nome in ("_quarto.yml", "ricerche/_metadata.yml", "chi-sono.qmd", "metodo.qmd",
                 ".zenodo.json", "CITATION.cff"):
        f = RADICE / nome
        if f.exists():
            tutto += leggi(f)
    orcid_finto = ORCID_FINTO in tutto
    if orcid_finto:
        promemoria.append(f"ORCID: c'è ancora il segnaposto {ORCID_FINTO}. In VS Code: "
                          f"Ctrl+Shift+H, cerca {ORCID_FINTO}, sostituisci con il tuo, "
                          f"«Sostituisci tutto».")

    if CI:
        if orcid_finto:
            print(f"::warning::ORCID ancora segnaposto ({ORCID_FINTO}): sostituiscilo prima "
                  f"di rendere raggiungibile il sito.")
        for e in errori:
            print(f"::error::{e}")
        print(f"Controllo: {len(errori)} errori, {len(promemoria)} promemoria.")
        for p in promemoria:
            print("  - " + p)
        return 1 if errori else 0

    print("CONTROLLO PRIMA DI PUBBLICARE")
    print("=============================")
    if errori:
        print(f"\nDA CORREGGERE ({len(errori)}) — con questi GitHub rifiuta la pubblicazione:")
        for e in errori:
            print("  ✗ " + e)
    if promemoria:
        print(f"\nPROMEMORIA ({len(promemoria)}) — non bloccano nulla:")
        for p in promemoria:
            print("  · " + p)
    if not errori and not promemoria:
        print("\nTutto a posto: non manca nulla.")
    elif not errori:
        print("\nNessun errore: puoi fare Commit e Sync.")
    print("\nI riquadri DA COMPLETARE si vedono solo nell'anteprima: sul sito pubblico")
    print("vengono tolti da soli. Le pagine con «draft: true» non vengono pubblicate.")
    return 1 if errori else 0


if __name__ == "__main__":
    try:
        codice = main()
    finally:
        attendi_invio()
    sys.exit(codice)
