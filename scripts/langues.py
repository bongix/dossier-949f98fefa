#!/usr/bin/env python3
"""Detection des langues demandees dans le texte d'une annonce.

Renvoie, par langue, le niveau d'exigence : "requis" ou "atout".
Le luxembourgeois et l'allemand sont les deux filtres decisifs pour ce profil.
"""
import re
import unicodedata

LANGUES = {
    "FR": r"fran[cç]ais|french|franz[oö]sisch|langue fran[cç]aise",
    "EN": r"anglais|english|englisch|langue anglaise",
    "DE": r"allemand|german\b|deutsch|langue allemande",
    "LU": r"luxembourgeois|luxembourgish|l[eë]tzebuergesch|luxemburgisch|langue luxembourgeoise",
    "NL": r"n[eé]erlandais|dutch|niederl[aä]ndisch|flamand",
    "IT": r"italien\b|italian\b|italienisch",
    "ES": r"espagnol|spanish|spanisch",
    "PT": r"portugais|portuguese|portugiesisch",
    "PL": r"polonais|polish|polnisch",
    "RU": r"russe\b|russian|russisch",
    "ZH": r"chinois|mandarin|chinese",
    "SV": r"su[eé]dois|swedish",
    "EL": r"grec\b|greek",
    "RO": r"roumain|romanian",
    "AR": r"arabe\b|arabic",
}

# abreviations du type FR/EN, EN-DE, "FR/DE/EN"
ABREV = {"fr": "FR", "en": "EN", "gb": "EN", "uk": "EN", "de": "DE", "all": "DE",
         "lu": "LU", "lb": "LU", "nl": "NL", "it": "IT", "es": "ES", "pt": "PT"}

# "Maitrise de deux des langues suivantes : luxembourgeois / francais / allemand /
# anglais" est une formule courante au Luxembourg : elle n'exige pas les quatre.
AU_CHOIX = (r"(?:une|deux|trois|2|3)\s+des\s+(?:\w+\s+){0,2}langues|l['e]une des langues|"
            r"parmi les langues|au moins deux langues|two of the following|"
            r"one of the following languages|at least two of|zwei der folgenden")

# "luxembourgeois" designe le plus souvent le pays ou le droit, pas la langue.
LU_FAUX_AMI = (r"(?:comptabilit|droit|march|societ|soci[eé]t|legislation|l[eé]gislation|fiscalit|"
               r"reglementation|r[eé]glementation|place|norme|plan comptable|entreprise|client|"
               r"banque|secteur|autorit|gouvernement|territoire|resident|r[eé]sident|gaap|"
               r"gestionnaire|employeur|filiale|etablissement|[eé]tablissement)\w*\s+"
               r"luxembourgeoise?s?")
LANG_CUE = r"langue|parl|[eé]crit|oral|courant|ma[iî]tris|connaissance|bilingue|trilingue|niveau"

ATOUT = (r"atout|un plus|est un plus|serait un plus|souhait|appreci|"
         r"is a plus|a plus\b|an asset|considered an asset|advantage|nice to have|"
         r"von vorteil|w[uü]nschenswert|optional|id[eé]alement|de pr[eé]f[eé]rence|"
         r"bonus|would be|serait appreci|constitue un atout")
REQUIS = (r"courant|fluent|ma[iî]tris|obligatoire|indispensable|imp[eé]ratif|"
          r"excellente connaissance|parfaite|required|mandatory|must\b|"
          r"verhandlungssicher|flie[sß]end|sehr gute|tr[eè]s bonne connaissance|"
          r"niveau c1|niveau c2|\bc1\b|\bc2\b|\bb2\b|bilingue|trilingue|"
          r"langue de travail|working language|proficien")


def norm(s):
    s = unicodedata.normalize("NFD", (s or "").lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


ORDRE = {"requis": 3, "choix": 2, "atout": 1}


def detecter(texte):
    """-> dict {code: 'requis'|'choix'|'atout'} pour chaque langue mentionnee.

    'choix' = la langue figure dans une enumeration du type "deux des langues
    suivantes" : elle n'est pas exigee individuellement.
    """
    t = norm(texte)
    out = {}

    def poser(code, niveau):
        if ORDRE[niveau] > ORDRE.get(out.get(code, "atout"), 0) or code not in out:
            out[code] = niveau

    for code, motif in LANGUES.items():
        for m in re.finditer(motif, t):
            a, b = max(0, m.start() - 140), min(len(t), m.end() + 140)
            fenetre = t[a:b]
            phrases = re.split(r"[.;•\n]", fenetre)
            proche = next((p for p in phrases if re.search(motif, p)), fenetre)

            # le luxembourgeois ne compte que s'il s'agit bien de la langue
            if code == "LU":
                brut = t[max(0, m.start() - 40):m.end() + 5]
                if re.search(LU_FAUX_AMI, brut):
                    continue
                if not re.search(r"letzebuergesch|luxembourgish|luxemburgisch|langue luxembourgeoise", t):
                    autres = sum(1 for c2, mo in LANGUES.items()
                                 if c2 != "LU" and re.search(mo, proche))
                    if not (autres >= 1 and re.search(LANG_CUE, proche)):
                        continue

            if re.search(AU_CHOIX, proche):
                poser(code, "choix")
            elif re.search(ATOUT, proche):
                poser(code, "atout")
            elif re.search(REQUIS, proche) or re.search(REQUIS, fenetre):
                poser(code, "requis")
            else:
                poser(code, "atout")

    # groupes du type "FR/EN", "DE-FR", "EN / FR / DE"
    for grp in re.findall(r"\b((?:fr|en|de|lu|lb|nl|it|es|pt|gb|uk|all)"
                          r"(?:\s*[/|\-]\s*(?:fr|en|de|lu|lb|nl|it|es|pt|gb|uk|all)){1,3})\b", t):
        for tok in re.split(r"[/|\-]", grp):
            code = ABREV.get(tok.strip())
            if code:
                out[code] = "requis"

    return out


def resume(langues):
    """Etiquette courte, par exemple 'EN + FR (DE + LU en atout)'."""
    if not langues:
        return "non precise"
    req = sorted(c for c, n in langues.items() if n == "requis")
    ch = sorted(c for c, n in langues.items() if n == "choix")
    at = sorted(c for c, n in langues.items() if n == "atout")
    bouts = []
    if req:
        bouts.append(" + ".join(req))
    if ch:
        bouts.append("2 parmi " + " / ".join(ch))
    if at:
        bouts.append("(" + " + ".join(at) + " en atout)")
    return " ".join(bouts)


def accessible(langues):
    """Le poste est-il atteignable avec le francais et l'anglais seulement ?

    Une enumeration "deux des langues suivantes" passe des que le francais ou
    l'anglais y figure ; un atout ne bloque jamais.
    """
    durs = {c for c, n in langues.items() if n == "requis"} - {"FR", "EN"}
    if durs:
        return False
    ch = {c for c, n in langues.items() if n == "choix"}
    return not ch or bool(ch & {"FR", "EN"})
