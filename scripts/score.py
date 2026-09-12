#!/usr/bin/env python3
"""Scoring des offres pour le profil AK (autiste, 50 ans, Sandweiler).

5 axes, 100 points. Le score n'est PAS un jugement de la qualite de l'offre :
c'est une estimation de la compatibilite sensorielle et cognitive du poste
avec un besoin de calme, de regles explicites et de faible charge sociale.
"""
import json
import re
import unicodedata
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SSM_NQ = 2771.33   # salaire social minimum non qualifie, 01.06.2026
SSM_Q = 3325.59    # salaire social minimum qualifie, 01.06.2026

# --- distances routieres approximatives depuis Sandweiler (km) -------------
KM = {
    "findel": 3, "hamm": 4, "contern": 4, "cents": 5, "munsbach": 5, "moutfort": 5,
    "senningerberg": 5, "neudorf": 6, "niederanven": 6, "kirchberg": 7, "bonnevoie": 7,
    "oetrange": 6, "luxembourg": 8, "howald": 8, "hesperange": 8, "itzig": 6,
    "gasperich": 10, "cloche d'or": 10, "belair": 10, "merl": 11, "walferdange": 12,
    "junglinster": 12, "betzdorf": 12, "roodt": 14, "strassen": 13, "bertrange": 13,
    "leudelange": 14, "steinsel": 15, "bettembourg": 18, "capellen": 20,
    "grevenmacher": 20, "dudelange": 20, "remich": 20, "mamer": 17, "kockelscheuer": 12,
    "mondorf": 22, "foetz": 22, "schifflange": 22, "kayl": 22, "lintgen": 22,
    "wasserbillig": 22, "windhof": 24, "esch": 25, "mersch": 25, "echternach": 25,
    "belvaux": 27, "colmar-berg": 28, "bissen": 28, "sanem": 28, "bascharage": 28,
    "differdange": 33, "petange": 33, "rodange": 35, "ettelbruck": 35, "redange": 35,
    "diekirch": 38, "wiltz": 60, "clervaux": 70, "troisvierges": 80, "munshausen": 68,
    "rambrouch": 45, "useldange": 32,
}
ETRANGER = ("belgium", "belgique", "france", "allemagne", "germany", "lorraine",
            "saarland", "rheinland", "arlon", "thionville", "metz", "trier", "treves",
            "abroad", "etranger", "switzerland", "suisse", "zurich", "geneva")

# --- vocabulaire ----------------------------------------------------------
BRUIT = {  # environnement sensoriel defavorable
    "call center": -14, "call centre": -14, "centre d'appel": -14, "hotline": -12,
    "reception": -8, "accueil physique": -9, "accueil des visiteurs": -9,
    "welcome visitors": -9, "front office": -8, "front desk": -9, "standard telephonique": -10,
    "phone calls": -6, "appels entrants": -8, "showroom": -8, "magasin": -8, "retail": -8,
    "boutique": -8, "restaurant": -10, "cuisine": -10, "bar ": -8, "hotel": -7,
    "chantier": -12, "atelier de production": -9, "entrepot": -9, "warehouse": -9,
    "production line": -9, "ligne de production": -9, "open space": -5, "openspace": -5,
    "terrain": -6, "deplacements frequents": -6, "travel frequently": -6,
    "evenements": -5, "salon": -4, "clientele": -4,
}
CALME = {
    "back office": 12, "back-office": 12, "middle office": 9, "arriere-guichet": 10,
    "teletravail": 8, "home office": 8, "remote": 7, "hybride": 5, "hybrid": 5,
    "saisie": 7, "encodage": 7, "data entry": 8, "archivage": 8, "archives": 8,
    "numerisation": 7, "scanning": 6, "indexation": 7, "documentation": 5,
    "reconciliation": 8, "rapprochement": 7, "controle de qualite": 5,
    "analyse de donnees": 5, "traitement des dossiers": 6, "gestion documentaire": 7,
    "bureau": 2, "laboratoire": 3,
}
REGLES = {  # taches proceduralisees, cadre explicite
    "procedure": 7, "procedures": 7, "checklist": 6, "controle": 5, "conformite": 6,
    "compliance": 6, "reglementaire": 6, "regulatory": 6, "kyc": 7, "aml": 7,
    "lutte contre le blanchiment": 7, "rapprochement bancaire": 6, "reporting": 5,
    "verification": 6, "validation": 5, "audit": 4, "qualite des donnees": 6,
    "data quality": 6, "referentiel": 5, "nav": 5, "valorisation": 5,
    "comptabilisation": 6, "ecritures": 5, "facturation": 5, "declaration": 4,
    "processus etablis": 7, "instructions": 4, "methodique": 6, "rigueur": 6,
    "rigoureux": 6, "precision": 6, "detail-oriented": 7, "souci du detail": 7,
    "attention to detail": 7, "meticuleux": 7, "organise": 3,
}
FLOU = {  # environnement mouvant / implicite, couteux cognitivement
    "multitache": -7, "multitasking": -7, "priorites changeantes": -8,
    "environnement dynamique": -6, "fast-paced": -8, "fast paced": -8,
    "rythme soutenu": -7, "flexibilite": -4, "adaptabilite": -5, "polyvalent": -5,
    "polyvalence": -5, "imprevu": -6, "urgences": -6, "stress": -6,
    "sous pression": -8, "deadline serre": -5, "ambigu": -6, "startup": -4,
    "porter plusieurs casquettes": -8, "wear many hats": -8,
}
SOCIAL = {  # exposition sociale / hierarchique forte
    "relation client": -8, "client facing": -9, "customer facing": -9,
    "commercial": -9, "prospection": -10, "negociation": -8, "vente": -8, "sales": -9,
    "business development": -10, "manager une equipe": -10, "encadrer": -8,
    "management d'equipe": -10, "team lead": -8, "leadership": -6,
    "presentations": -5, "reunions clients": -6, "networking": -7,
    "conseil client": -7, "accompagner les clients": -6, "esprit d'equipe": -2,
}
AUTONOMIE = {
    "travail autonome": 7, "en autonomie": 6, "independamment": 5, "independently": 5,
    "concentration": 8, "travail de fond": 6, "sans supervision": 4,
    "temps partiel": 6, "part time": 6, "part-time": 6, "horaires flexibles": 5,
    "flexible hours": 5, "casque": 4,
}
PROFIL = {  # correspondance avec le parcours (finance, back-office, regulateur)
    "fonds": 6, "fund": 6, "opcvm": 6, "ucits": 6, "aifm": 5, "sicav": 5,
    "transfer agent": 8, "transfer agency": 8, "fund administration": 7,
    "depositary": 6, "custody": 6, "titres": 5, "securities": 5,
    "banque": 5, "bank": 5, "finance": 4, "financier": 4, "asset management": 5,
    "regulateur": 8, "regulator": 8, "cssf": 7, "csrd": 3, "amf": 8,
    "administratif": 5, "administrative": 5, "comptabilite": 5, "accounting": 5,
    "secretariat": 4, "assistant": 3, "gestionnaire": 4,
    "graphisme": 5, "graphic design": 5, "illustration": 6, "pao": 5,
    "indesign": 4, "photoshop": 3, "illustrator": 4, "mise en page": 4,
}
# Employeurs publics / para-publics : teste sur le NOM de l'employeur seulement.
PUBLIC = ("ministere", "administration communale", "commune de", "ville de luxembourg",
          "etat du grand-duche", "cfl", "post luxembourg", "luxtram", "creos",
          "commission de surveillance", "cssf", "banque centrale", "bcl",
          "european ", "europeenne", "eurocontrol", "eurostat", "parlement europeen",
          "cour de justice", "court of justice", "european investment", "\bbei\b",
          "fondation", "asbl", "a.s.b.l", "croix-rouge", "caritas", "elisabeth",
          "hopitaux", "hopital", "\bchl\b", "\bchem\b", "rehazenter", "laboratoire national",
          "ligue medico", "arcus", "solidarite jeunes", "inter-actions",
          "snca", "statec", "lycee", "universite du luxembourg", "uni.lu",
          "luxembourg institute", "\blist\b", "\blih\b", "\bliser\b",
          "luxinnovation", "snhbm", "fonds du logement", "\bsnci\b", "\badem\b",
          "chambre de commerce", "chambre des metiers", "chambre des salaries",
          "office national", "agence nationale", "institut national")
LANGUES_DURES = ("luxembourgeois", "letzebuergesch", "luxembourgish", "allemand courant",
                 "deutsch fliessend", "fluent german", "allemand indispensable",
                 "allemand obligatoire", "german is a must", "german mandatory")


def norm(s):
    s = unicodedata.normalize("NFD", (s or "").lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def pesee(txt, table, plancher, plafond):
    """Somme bornee des poids des expressions presentes, avec les motifs trouves."""
    total, motifs = 0, []
    for mot, poids in table.items():
        if mot in txt:
            total += poids
            motifs.append(mot)
    return max(plancher, min(plafond, total)), motifs


def distance(lieu):
    l = norm(lieu)
    if any(e in l for e in ETRANGER) and "luxembourg" not in l:
        return 60
    for ville, km in sorted(KM.items(), key=lambda x: -len(x[0])):
        if ville in l:
            return km
    return 15  # localite luxembourgeoise inconnue : hypothese mediane


# --- salaires de marche (brut annuel, base fixe, Luxembourg 2026) ----------
# Sources : guides de remuneration fonds/finance 2026, STATEC, grilles publiques.
MARCHE = [
    (r"transfer agen|registrar", (42000, 68000), "Transfer agency"),
    (r"fund account|comptab.*fonds|nav ", (45000, 70000), "Fund accounting"),
    (r"kyc|aml|blanchiment|financial crime", (45000, 70000), "KYC / AML"),
    (r"compliance|conformite", (55000, 85000), "Compliance"),
    (r"depositary|depositaire|custody", (45000, 72000), "Depositary / custody"),
    (r"risk|risque", (55000, 85000), "Risk"),
    (r"data analyst|business analyst|data scientist", (55000, 80000), "Data / analyse"),
    (r"data entry|encodage|saisie|operateur de saisie", (34000, 45000), "Saisie de donnees"),
    (r"archiv|documentalist|record manag", (40000, 55000), "Archives / documentation"),
    (r"payroll|salaire|paie", (48000, 68000), "Payroll"),
    (r"comptable|accountant|accounting", (45000, 68000), "Comptabilite"),
    (r"secretar|office manager|office administrator|assistant.*administrat|"
     r"administrative assistant|employe.*administratif", (38000, 52000), "Support administratif"),
    (r"back office|middle office|operations officer|settlement", (42000, 65000), "Back / middle office"),
    (r"graphi|design|illustrat|pao|layout|mise en page", (40000, 58000), "Creation graphique"),
    (r"quality|controle qualite|qc ", (40000, 58000), "Controle qualite"),
    (r"reporting|regulatory report", (50000, 75000), "Reporting reglementaire"),
    (r"logistic|warehouse|magasinier", (35000, 48000), "Logistique"),
    (r"juriste|legal|lawyer|avocat|paralegal", (55000, 90000), "Juridique"),
    (r"corporate officer|company secretar|domiciliation|corporate administrat",
     (45000, 68000), "Corporate / domiciliation"),
    (r"\bhr\b|ressources humaines|recruit|talent", (48000, 70000), "RH"),
    (r"treasury|tresorerie|cash manag", (50000, 75000), "Tresorerie"),
    (r"projet|project manag|\bpmo\b", (60000, 90000), "Gestion de projet"),
    (r"marketing|communication", (45000, 70000), "Marketing / communication"),
    (r"technicien|maintenance|electric|mecanic", (38000, 55000), "Technique"),
    (r"nettoyage|cleaning|agent d entretien", (30000, 38000), "Entretien"),
    (r"chauffeur|driver|livreur", (32000, 45000), "Transport"),
    (r"infirm|soignant|educateur|aide.soignant|psycholog", (45000, 70000), "Sante / social"),
    (r"enseignant|professeur|formateur|teacher|surveillant|vie scolaire",
     (42000, 65000), "Education"),
    (r"\bit\b|\bict\b|developer|developpeur|software|systeme?s? engineer|"
     r"devops|cyber|network|infrastructure", (55000, 85000), "IT"),
]


def salaire(offre):
    """(min, max, source) en brut annuel."""
    brut = offre.get("salaire_annonce", "")
    n = norm(brut)
    nombres = [float(x.replace(" ", "").replace(",", "")) for x in
               re.findall(r"\d[\d \.,]{2,}", n.replace(".00", ""))]
    nombres = [x for x in nombres if 1000 <= x <= 400000]
    if nombres and "sfr" not in n:
        mensuel = ("mois" in n or "month" in n or "/ mois" in n
                   or max(nombres) < 15000)
        lo, hi = min(nombres), max(nombres)
        if mensuel:
            lo, hi = lo * 13, hi * 13   # 13e mois usuel au Luxembourg
        if 20000 <= lo <= 400000:
            return int(lo), int(hi), "annonce"
    cible = norm(offre["titre"] + " " + offre.get("description", "")[:600])
    for motif, (lo, hi), _fam in MARCHE:
        if re.search(motif, cible):
            return lo, hi, "marche"
    return 40000, 60000, "marche"


def famille(offre):
    cible = norm(offre["titre"] + " " + offre.get("description", "")[:600])
    for motif, _f, nom in MARCHE:
        if re.search(motif, cible):
            return nom
    return "Autre"


def evalue(offre):
    txt = norm(offre["titre"] + " " + offre["employeur"] + " " +
               offre.get("description", ""))
    titre = norm(offre["titre"])
    motifs = {}

    # 1. environnement sensoriel /30
    b, m1 = pesee(txt, BRUIT, -28, 0)
    c, m2 = pesee(txt, CALME, 0, 22)
    sensoriel = max(0, min(30, 16 + b + c))
    motifs["bruit"], motifs["calme"] = m1, m2

    # 2. regles explicites /25
    r, m3 = pesee(txt, REGLES, 0, 20)
    f, m4 = pesee(txt, FLOU, -18, 0)
    cadre = max(0, min(25, 10 + r + f))
    motifs["regles"], motifs["flou"] = m3, m4

    # 3. faible exposition sociale /20
    s, m5 = pesee(txt, SOCIAL, -20, 0)
    a, m6 = pesee(txt, AUTONOMIE, 0, 12)
    if re.search(r"manager|head of|director|responsable|chef d", titre):
        s -= 8
    isolement = max(0, min(20, 14 + s + a))
    motifs["social"], motifs["autonomie"] = m5, m6

    # 4. adequation profil /15
    p, m7 = pesee(txt, PROFIL, 0, 15)
    adequation = max(0, min(15, p))
    motifs["profil"] = m7

    # 5. praticite /10
    km = distance(offre["lieu"])
    prat = 6 if km <= 10 else 5 if km <= 15 else 3 if km <= 25 else 1 if km <= 40 else 0
    contrat = offre.get("contrat", "")
    prat += 2 if contrat == "Permanent" else 1 if contrat == "Contract" else 0
    if "Part Time" in offre.get("horaire", ""):
        prat += 2
    if any(l in txt for l in LANGUES_DURES):
        prat -= 3
    if re.search(r"internship|student job|traineeship|apprentic", norm(contrat)):
        prat -= 3
    praticite = max(0, min(10, prat))

    lo, hi, src = salaire(offre)
    nom = " " + norm(offre["employeur"]) + " "
    pub = any(re.search(k, nom) if "\\b" in k else k in nom for k in PUBLIC)

    offre.update({
        "score": sensoriel + cadre + isolement + adequation + praticite,
        "axes": {"sensoriel": sensoriel, "cadre": cadre, "isolement": isolement,
                 "adequation": adequation, "praticite": praticite},
        "km_sandweiler": km,
        "salaire_min": lo, "salaire_max": hi, "salaire_source": src,
        "famille": famille(offre),
        "secteur_public": pub,
        "motifs": {k: v[:6] for k, v in motifs.items() if v},
        "signaux_negatifs": (m1 + m4 + m5)[:8],
    })
    return offre


def main():
    offres = json.loads((RACINE / "data" / "offres_brutes.json").read_text(encoding="utf-8"))
    for o in offres:
        evalue(o)
    # on ecarte les stages et les postes clairement hors marche luxembourgeois
    offres = [o for o in offres
              if not re.search(r"internship|student job|traineeship|apprentic",
                               norm(o.get("contrat", "")))
              and not re.search(r"\bintern\b|stagiaire|apprenti|graduate programme|"
                                r"working student|etudiant", norm(o["titre"]))
              and o["km_sandweiler"] < 60]
    offres.sort(key=lambda o: -o["score"])
    for rang, o in enumerate(offres, 1):
        o["rang"] = rang
        o.pop("description", None)
    sortie = RACINE / "data" / "offres_classees.json"
    sortie.write_text(json.dumps(offres, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(offres)} offres classees -> {sortie}")
    for o in offres[:20]:
        print(f"{o['score']:3d}  {o['titre'][:48]:50s} {o['employeur'][:26]:28s} "
              f"{o['km_sandweiler']:2d}km {o['salaire_min']//1000}-{o['salaire_max']//1000}k")


if __name__ == "__main__":
    main()
