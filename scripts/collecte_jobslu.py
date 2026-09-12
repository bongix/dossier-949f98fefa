#!/usr/bin/env python3
"""Collecte des offres jobs.lu correspondant au profil AK.

jobs.lu est la seule grande plateforme luxembourgeoise accessible sans
authentification ni anti-bot (ADEM JobBoard = login, GovJobs = captcha,
Moovijob / Monster / Indeed = Cloudflare). Voir docs/SOURCES.md.
"""
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
BASE = "https://en.jobs.lu"

# Requêtes choisies d'après le profil : finance back-office (son passé),
# travail administratif procédural, documentation/données, et créatif.
REQUETES = [
    "back office", "middle office", "transfer agent", "fund administration",
    "fund accounting", "reconciliation", "corporate actions", "custody",
    "KYC", "AML", "compliance officer", "regulatory reporting", "onboarding client",
    "data entry", "encodage", "saisie", "archiviste", "documentaliste", "scanning",
    "assistant administratif", "employe administratif", "secretariat", "back-office assistant",
    "comptable", "accounting assistant", "facturation", "payroll",
    "data quality", "data analyst", "reporting", "controle", "quality control",
    "graphiste", "designer", "illustration", "PAO", "mise en page",
    "bibliothecaire", "traduction", "proofreading", "relecture",
    "part time", "temps partiel",
]

MOIS = {"january":1,"february":2,"march":3,"april":4,"may":5,"june":6,"july":7,
        "august":8,"september":9,"october":10,"november":11,"december":12}


def get(url, essais=3):
    for n in range(essais):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA,
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
            })
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", "ignore")
        except Exception as e:
            if n == essais - 1:
                print(f"  ! echec {url}: {e}", file=sys.stderr)
                return ""
            time.sleep(2 * (n + 1))
    return ""


def texte(h):
    h = re.sub(r"<script.*?</script>|<style.*?</style>", " ", h, flags=re.S | re.I)
    h = re.sub(r"<[^>]+>", " ", h)
    return re.sub(r"\s+", " ", html.unescape(h)).strip()


def liste(requete):
    """Renvoie les offres de la page de résultats pour une requête."""
    url = f"{BASE}/Jobs.aspx?Keywords={urllib.parse.quote(requete)}"
    page = get(url)
    out = []
    for bloc in re.findall(r'<article class="job-list-item.*?</article>', page, re.S):
        oid = re.search(r'id="job-id-(\d+)"', bloc)
        titre = re.search(r'class="job-title"[^>]*>(.*?)</a>', bloc, re.S)
        boite = re.search(r'class="recruiter-name"[^>]*>(.*?)</a>', bloc, re.S)
        lieu = re.search(r'<span class="location">(.*?)</span>', bloc, re.S)
        date = re.search(r'<span class="date">(.*?)</span>', bloc, re.S)
        if not (oid and titre):
            continue
        out.append({
            "id": oid.group(1),
            "titre": texte(titre.group(1)),
            "employeur": texte(boite.group(1)) if boite else "",
            "lieu": texte(lieu.group(1)) if lieu else "",
            "vu_le": texte(date.group(1)) if date else "",
            "requete": requete,
            "url": f"{BASE}/ApplyForJob.aspx?Id={oid.group(1)}",
        })
    return out


def detail(offre):
    page = get(offre["url"])
    if not page:
        return offre
    t = texte(page)
    i = t.find("Return to Job Search")
    corps = t[i:] if i > 0 else t
    corps = corps.split("Similar Jobs")[0][:12000]

    def champ(nom, suite):
        m = re.search(nom + r"\s*:\s*(.*?)\s*(?:" + suite + ")", corps)
        return m.group(1).strip() if m else ""

    offre["salaire_annonce"] = champ("Payment", "Last updated|Contract Type|Hours|Apply Now")
    offre["contrat"] = champ("Contract Type", "Hours|Apply Now|Share this job")
    offre["horaire"] = champ("Hours", "Apply Now|Share this job")
    offre["maj"] = champ("Last updated", "Contract Type|Hours|Apply Now")
    d = corps.find("Job Description")
    txt = corps[d + len("Job Description"):d + 12000] if d > 0 else corps[:10000]
    offre["description"] = couper(txt)
    return offre


# Le formulaire de candidature de jobs.lu est colle a la fin de chaque annonce et
# contient "Insert English/French/German/Luxembourgish Cover note" : sans coupe,
# toute offre parait exiger quatre langues.
FIN = ("Apply for this job", "Are you legally authorized", "Add default jobs.lu cover note",
       "Cover Note", "First Name", "Send me similar jobs", "Report this job",
       "Related Sectors:", "Related Locations:")


def couper(txt):
    fins = [txt.find(m) for m in FIN]
    fins = [i for i in fins if i > 200]
    return txt[:min(fins)].strip() if fins else txt.strip()


def main():
    vues, offres = set(), []
    for q in REQUETES:
        res = liste(q)
        neuves = [o for o in res if o["id"] not in vues]
        for o in neuves:
            vues.add(o["id"])
        offres.extend(neuves)
        print(f"{q:28s} {len(res):3d} resultats, {len(neuves):3d} nouvelles (total {len(offres)})")
        time.sleep(0.6)

    print(f"\nDetail de {len(offres)} offres...")
    for n, o in enumerate(offres, 1):
        detail(o)
        if n % 25 == 0:
            print(f"  {n}/{len(offres)}")
        time.sleep(0.4)

    sortie = RACINE / "data" / "offres_brutes.json"
    sortie.write_text(json.dumps(offres, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{len(offres)} offres -> {sortie}")


if __name__ == "__main__":
    main()
