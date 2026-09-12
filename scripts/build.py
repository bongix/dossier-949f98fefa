#!/usr/bin/env python3
"""Genere index.html a partir de data/dossier.json et data/offres_classees.json."""
import html
import json
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
D = json.loads((RACINE / "data" / "dossier.json").read_text(encoding="utf-8"))
OFFRES = json.loads((RACINE / "data" / "offres_classees.json").read_text(encoding="utf-8"))
E = lambda s: html.escape(str(s or ""))

CSS = """
*,*::before,*::after{box-sizing:border-box}
:root{
  --fond:#f7f5f1; --carte:#fffdfa; --bord:#e2ddd4; --bord-fort:#cfc8bc;
  --texte:#2f2c28; --doux:#6b655d; --tres-doux:#928b81;
  --accent:#4a6b5f; --accent-doux:#e6eeea; --accent-texte:#2f4a41;
  --chaud:#8a6a3d; --chaud-doux:#f3ece0;
  --alerte:#8a4f4f; --alerte-doux:#f5e9e9;
  --r:10px; --max:1060px;
}
:root:not([data-theme="light"]){ }
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --fond:#1c1b19; --carte:#232220; --bord:#35332f;
    --bord-fort:#47443f; --texte:#e6e1d8; --doux:#a8a196; --tres-doux:#807a71;
    --accent:#8fb3a4; --accent-doux:#253029; --accent-texte:#a9c9bb;
    --chaud:#c2a06c; --chaud-doux:#302819;
    --alerte:#c98f8f; --alerte-doux:#332424;
  }
}
:root[data-theme="dark"]{
  --fond:#1c1b19; --carte:#232220; --bord:#35332f; --bord-fort:#47443f;
  --texte:#e6e1d8; --doux:#a8a196; --tres-doux:#807a71;
  --accent:#8fb3a4; --accent-doux:#253029; --accent-texte:#a9c9bb;
  --chaud:#c2a06c; --chaud-doux:#302819;
  --alerte:#c98f8f; --alerte-doux:#332424;
}
body{margin:0;background:var(--fond);color:var(--texte);
 font:16px/1.65 ui-sans-serif,-apple-system,"Segoe UI",Inter,system-ui,sans-serif;
 -webkit-font-smoothing:antialiased}
.wrap{max-width:var(--max);margin:0 auto;padding:0 20px}
header.top{padding:54px 0 30px;border-bottom:1px solid var(--bord)}
h1{font-size:clamp(26px,4.2vw,38px);line-height:1.2;margin:0 0 10px;letter-spacing:-.02em;font-weight:650}
.sous{color:var(--doux);font-size:17px;max-width:62ch;margin:0}
.meta{margin-top:18px;color:var(--tres-doux);font-size:13.5px}
nav.som{display:flex;flex-wrap:wrap;gap:8px;margin:26px 0 0}
nav.som a{font-size:13.5px;text-decoration:none;color:var(--accent-texte);
 background:var(--accent-doux);padding:5px 11px;border-radius:99px;border:1px solid transparent}
nav.som a:hover{border-color:var(--accent)}
section{padding:44px 0;border-bottom:1px solid var(--bord)}
section:last-of-type{border-bottom:0}
h2{font-size:24px;margin:0 0 6px;letter-spacing:-.015em;font-weight:640}
h2 .num{color:var(--tres-doux);font-weight:400;margin-right:10px;font-variant-numeric:tabular-nums}
h3{font-size:17px;margin:30px 0 10px;font-weight:620}
.chapo{color:var(--doux);max-width:70ch;margin:0 0 22px}
p{max-width:74ch}
ul{padding-left:20px}li{margin:7px 0;max-width:72ch}
a{color:var(--accent-texte)}
.carte{background:var(--carte);border:1px solid var(--bord);border-radius:var(--r);padding:18px 20px;margin:12px 0}
.grille{display:grid;gap:12px}
@media(min-width:720px){.g2{grid-template-columns:1fr 1fr}.g3{grid-template-columns:repeat(3,1fr)}}
.encadre{background:var(--accent-doux);border:1px solid transparent;border-left:3px solid var(--accent);
 border-radius:var(--r);padding:16px 20px;margin:18px 0}
.encadre.warn{background:var(--alerte-doux);border-left-color:var(--alerte)}
.encadre.warm{background:var(--chaud-doux);border-left-color:var(--chaud)}
.encadre p{margin:0}
.etiq{display:inline-block;font-size:11.5px;letter-spacing:.04em;text-transform:uppercase;
 padding:2px 8px;border-radius:99px;background:var(--accent-doux);color:var(--accent-texte);
 border:1px solid var(--bord);white-space:nowrap}
.etiq.pub{background:var(--chaud-doux);color:var(--chaud)}
.etiq.neutre{background:transparent;color:var(--doux)}
table{width:100%;border-collapse:collapse;font-size:14px}
.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch;border:1px solid var(--bord);
 border-radius:var(--r);background:var(--carte)}
th,td{padding:9px 12px;text-align:left;border-bottom:1px solid var(--bord);vertical-align:top}
th{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--doux);font-weight:600;
 position:sticky;top:0;background:var(--carte);z-index:1}
tr:last-child td{border-bottom:0}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.score{display:inline-block;min-width:34px;text-align:center;font-variant-numeric:tabular-nums;
 font-weight:640;padding:2px 6px;border-radius:6px;background:var(--accent-doux);color:var(--accent-texte)}
.score.b{opacity:.82}.score.c{background:transparent;color:var(--doux);font-weight:500}
.filtres{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:0 0 14px}
.filtres input,.filtres select{font:inherit;font-size:14px;padding:7px 10px;border:1px solid var(--bord-fort);
 border-radius:8px;background:var(--carte);color:var(--texte)}
.filtres input[type=search]{min-width:220px;flex:1}
.compte{color:var(--doux);font-size:13.5px;margin-left:auto}
.top{display:grid;gap:12px}
@media(min-width:780px){.top{grid-template-columns:1fr 1fr}}
.offre{background:var(--carte);border:1px solid var(--bord);border-radius:var(--r);padding:16px 18px}
.offre .ligne1{display:flex;gap:10px;align-items:flex-start;justify-content:space-between}
.offre h4{margin:0;font-size:16px;font-weight:620;line-height:1.35}
.offre h4 a{text-decoration:none;color:var(--texte)}
.offre h4 a:hover{color:var(--accent-texte);text-decoration:underline}
.offre .emp{color:var(--doux);font-size:14px;margin:3px 0 10px}
.offre dl{display:grid;grid-template-columns:auto 1fr;gap:2px 12px;margin:0;font-size:13.5px}
.offre dt{color:var(--tres-doux)}.offre dd{margin:0}
.barres{margin-top:12px;display:grid;gap:4px}
.barre{display:grid;grid-template-columns:92px 1fr auto;gap:8px;align-items:center;font-size:12px;color:var(--doux)}
.piste{height:5px;border-radius:99px;background:var(--bord);overflow:hidden}
.piste i{display:block;height:100%;background:var(--accent);border-radius:99px}
.pas{color:var(--doux);font-size:13.5px;margin-top:10px}
.pas b{color:var(--alerte);font-weight:600}
footer{padding:36px 0 70px;color:var(--tres-doux);font-size:13.5px}
.theme{position:fixed;right:14px;bottom:14px;font:inherit;font-size:13px;padding:7px 12px;
 border:1px solid var(--bord-fort);border-radius:99px;background:var(--carte);color:var(--doux);cursor:pointer}
ol.plan{list-style:none;padding:0;counter-reset:p}
ol.plan>li{background:var(--carte);border:1px solid var(--bord);border-radius:var(--r);
 padding:16px 20px;margin:10px 0}
ol.plan>li>b{display:block;font-size:13px;text-transform:uppercase;letter-spacing:.05em;
 color:var(--accent-texte);margin-bottom:6px}
.small{font-size:13.5px;color:var(--doux)}
.acces{display:inline-block;font-size:11.5px;padding:2px 8px;border-radius:99px;white-space:nowrap;
 border:1px solid var(--bord)}
.acces.ok{background:var(--accent-doux);color:var(--accent-texte)}
.acces.prioritaire{background:var(--accent);color:var(--carte);border-color:transparent;font-weight:600}
.acces.compte,.acces.captcha{background:var(--alerte-doux);color:var(--alerte)}
.acces.langue{background:var(--chaud-doux);color:var(--chaud)}
.liens{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 6px;padding:0;list-style:none}
.liens a{display:inline-block;font-size:13.5px;text-decoration:none;padding:6px 12px;border-radius:8px;
 background:var(--carte);border:1px solid var(--bord-fort);color:var(--accent-texte)}
.liens a:hover{border-color:var(--accent)}
td .src{font-weight:600}
td a.src{text-decoration:none}
td a.src:hover{text-decoration:underline}
"""


def barre(nom, val, maxi):
    pct = round(100 * val / maxi)
    return (f'<div class="barre"><span>{nom}</span><span class="piste">'
            f'<i style="width:{pct}%"></i></span><span>{val}/{maxi}</span></div>')


def carte_offre(o):
    ax = o["axes"]
    sal = f'{o["salaire_min"]//1000}–{o["salaire_max"]//1000} k€'
    src = "annoncé" if o["salaire_source"] == "annonce" else "estimation marché"
    neg = o.get("signaux_negatifs") or []
    pub = '<span class="etiq pub">secteur public</span>' if o["secteur_public"] else ""
    return f"""<article class="offre">
 <div class="ligne1">
  <h4><a href="{E(o['url'])}" target="_blank" rel="noopener">{E(o['titre'])}</a></h4>
  <span class="score">{o['score']}</span>
 </div>
 <p class="emp">{E(o['employeur'])} — {E(o['lieu'])} {pub}</p>
 <dl>
  <dt>Contrat</dt><dd>{E(o['contrat'])} · {E(o['horaire'])}</dd>
  <dt>Salaire</dt><dd>{sal} <span class="small">({src})</span></dd>
  <dt>Trajet</dt><dd>≈ {o['km_sandweiler']} km depuis Sandweiler</dd>
  <dt>Famille</dt><dd>{E(o['famille'])}</dd>
 </dl>
 <div class="barres">
  {barre("Calme", ax['sensoriel'], 30)}
  {barre("Règles claires", ax['cadre'], 25)}
  {barre("Peu d'exposition", ax['isolement'], 20)}
  {barre("Profil", ax['adequation'], 15)}
  {barre("Praticité", ax['praticite'], 10)}
 </div>
 {f'<p class="pas">À vérifier : <b>{E(", ".join(neg[:4]))}</b></p>' if neg else ''}
</article>"""


def main():
    p, m, pu, mi, co, pl = (D["profil"], D["marche"], D["publics"],
                            D["missions"], D["communication"], D["plan"])
    lv, cs = D["levier"], D["consulter"]
    top = OFFRES[:12]
    familles = sorted({o["famille"] for o in OFFRES})
    contrats = sorted({o["contrat"] for o in OFFRES if o["contrat"]})

    lignes = "\n".join(
        f'<tr data-s="{o["score"]}" data-f="{E(o["famille"])}" data-c="{E(o["contrat"])}"'
        f' data-p="{1 if o["secteur_public"] else 0}" data-km="{o["km_sandweiler"]}"'
        f' data-t="{E((o["titre"] + " " + o["employeur"]).lower())}">'
        f'<td class="num"><span class="score {"b" if o["score"]<70 else ""}{"c" if o["score"]<50 else ""}">'
        f'{o["score"]}</span></td>'
        f'<td><a href="{E(o["url"])}" target="_blank" rel="noopener">{E(o["titre"])}</a>'
        f'{" <span class=\'etiq pub\'>public</span>" if o["secteur_public"] else ""}</td>'
        f'<td>{E(o["employeur"])}</td>'
        f'<td>{E(o["famille"])}</td>'
        f'<td>{E(o["contrat"])}{"" if o["horaire"]=="Full Time" else " · temps partiel possible"}</td>'
        f'<td class="num">{o["salaire_min"]//1000}–{o["salaire_max"]//1000} k€</td>'
        f'<td class="num">{o["km_sandweiler"]}</td></tr>'
        for o in OFFRES)

    grille = "\n".join(
        f'<tr><td><b>{E(g["famille"])}</b><br><span class="small">{E(g["note"])}</span></td>'
        f'<td class="num">{E(g["junior"])}</td><td class="num">{E(g["confirme"])}</td>'
        f'<td class="num">{E(g["senior"])}</td></tr>' for g in m["grille"])

    emp = "\n".join(
        f'<article class="carte"><div class="ligne1" style="display:flex;justify-content:space-between;'
        f'gap:10px;align-items:flex-start"><h4 style="margin:0;font-size:16px;font-weight:620">{E(e["nom"])}</h4>'
        f'<span class="etiq{" pub" if "haute" in e["priorite"] else " neutre"}">{E(e["priorite"])}</span></div>'
        f'<p class="small" style="margin:4px 0 8px">{E(e["lieu"])} · ≈ {e["km"]} km</p>'
        f'<p style="margin:0 0 8px">{E(e["pourquoi"])}</p>'
        f'<p class="small" style="margin:0"><b>Canal :</b> {E(e["canal"])}</p></article>'
        for e in pu["employeurs"])

    opts = "\n".join(
        f'<article class="carte"><div style="display:flex;justify-content:space-between;gap:10px;'
        f'align-items:flex-start"><h4 style="margin:0;font-size:17px;font-weight:620">{E(o["nom"])}</h4>'
        f'<span class="etiq">réalisme {E(o["realisme"])}</span></div>'
        f'<p class="small" style="margin:6px 0 12px"><b>Revenu :</b> {E(o["revenu"])}</p>'
        f'<p><b>Pourquoi ça colle.</b> {E(o["pourquoi"])}</p>'
        f'<p><b>Comment s\'y prendre.</b> {E(o["comment"])}</p>'
        f'<p style="margin-bottom:0"><b>Réserves.</b> {E(o["reserves"])}</p></article>'
        for o in mi["options"])

    comp = "\n".join(
        f'<tr><td><b>{E(c["quoi"])}</b><br><span class="small">{E(c["pourquoi"])}</span></td>'
        f'<td>{E(c["duree"])}</td><td>{E(c["ou"])}</td></tr>'
        for c in mi["competences"]["liste"])

    liens_eu = "".join(
        f'<li><a href="{E(l["u"])}" target="_blank" rel="noopener">{E(l["l"])}</a></li>'
        for l in cs["decouverte"]["liens"])

    src_lignes = "\n".join(
        f'<tr><td><a class="src" href="{E(r["url"])}" target="_blank" rel="noopener">{E(r["nom"])}</a></td>'
        f'<td><span class="acces {E(r["niveau"])}">{E(r["acces"])}</span></td>'
        f'<td>{E(r["contenu"])}</td><td>{E(r["faire"])}</td>'
        f'<td class="small" style="white-space:nowrap">{E(r["rythme"])}</td></tr>'
        for r in cs["lignes"])

    phases = "\n".join(
        f'<li><b>{E(f["periode"])}</b><ul>' +
        "".join(f"<li>{E(a)}</li>" for a in f["actions"]) + "</ul></li>"
        for f in pl["phases"])

    avantages = "\n".join(
        f'<article class="carte"><h4 style="margin:0 0 6px;font-size:16px;font-weight:620">{E(a["titre"])}</h4>'
        f'<p style="margin:0">{E(a["detail"])}</p></article>' for a in lv["avantages"])

    doc = f"""<title>Dossier emploi adapté — Luxembourg</title>
<meta name="robots" content="noindex,nofollow">
<meta name="description" content="Dossier de recherche d'emploi adapté au Luxembourg : offres classées, droits, pistes indépendantes.">
<style>{CSS}</style>

<header class="top"><div class="wrap">
 <h1>Un travail qui tient : dossier emploi adapté, Luxembourg</h1>
 <p class="sous">Deux pistes menées en parallèle — un emploi salarié dans un environnement réellement
 supportable, et des revenus propres hors contrat de travail. Les offres sont classées non pas par
 prestige ou par salaire, mais par compatibilité sensorielle et cognitive.</p>
 <p class="meta">Collecte du {date.today().strftime('%d/%m/%Y')} · {len(OFFRES)} offres analysées ·
 855 offres supplémentaires dépouillées pour les signaux de marché · page privée, non indexée</p>
 <nav class="som">
  <a href="#levier">1. Le levier à activer</a>
  <a href="#plan">2. Plan 90 jours</a>
  <a href="#offres">3. Offres classées</a>
  <a href="#public">4. Piste publique et européenne</a>
  <a href="#salaires">5. Salaires du marché</a>
  <a href="#missions">6. Missions digitales</a>
  <a href="#parler">7. Comment en parler</a>
  <a href="#consulter">8. Où chercher soi-même</a>
  <a href="#methode">9. Méthode et sources</a>
 </nav>
</div></header>

<main class="wrap">

<section id="profil">
 <h2><span class="num">0</span>Le point de départ</h2>
 <p class="chapo">{E(p['resume'])}</p>
 <div class="grille g2">
  <div class="carte"><h3 style="margin-top:0">Ce qui joue en faveur</h3><ul>
   {''.join(f'<li>{E(x)}</li>' for x in p['atouts'])}</ul></div>
  <div class="carte"><h3 style="margin-top:0">Ce qui doit être écarté d'emblée</h3><ul>
   {''.join(f'<li>{E(x)}</li>' for x in p['contraintes'])}</ul></div>
 </div>
</section>

<section id="levier">
 <h2><span class="num">1</span>{E(lv['titre'])}</h2>
 <p class="chapo">{E(lv['pourquoi'])}</p>
 <div class="encadre"><p><b>Critère d'éligibilité.</b> {E(lv['criteres'])}</p></div>
 <h3>La démarche, dans l'ordre</h3>
 <ol>{''.join(f'<li>{E(x)}</li>' for x in lv['procedure'])}</ol>
 <h3>Ce que le statut débloque</h3>
 <div class="grille g2">{avantages}</div>
 <div class="encadre warn"><p>{E(lv['avertissement'])}</p></div>
</section>

<section id="plan">
 <h2><span class="num">2</span>{E(pl['titre'])}</h2>
 <p class="chapo">Trois choses avancent en parallèle : un dossier administratif long à instruire,
 des candidatures immédiates, et une source de revenu indépendante qui met des mois à démarrer.
 Aucune des trois ne peut attendre les deux autres.</p>
 <ol class="plan">{phases}</ol>
</section>

<section id="offres">
 <h2><span class="num">3</span>Offres classées par compatibilité</h2>
 <p class="chapo">{len(OFFRES)} offres luxembourgeoises relevées et lues intégralement, puis notées sur
 100 selon cinq axes : calme de l'environnement (30), clarté des règles (25), faible exposition
 sociale (20), adéquation au parcours (15), praticité — trajet, contrat, langues (10). Le score
 mesure la <em>supportabilité</em>, pas la qualité de l'offre.</p>

 <h3>Les douze premières</h3>
 <div class="top">{''.join(carte_offre(o) for o in top)}</div>

 <h3>Le classement complet</h3>
 <div class="filtres">
  <input type="search" id="q" placeholder="Filtrer par intitulé ou employeur…" aria-label="Recherche">
  <select id="f"><option value="">Toutes les familles</option>
   {''.join(f'<option>{E(x)}</option>' for x in familles)}</select>
  <select id="c"><option value="">Tous les contrats</option>
   {''.join(f'<option>{E(x)}</option>' for x in contrats)}</select>
  <select id="s"><option value="0">Tous les scores</option><option value="70">70 et plus</option>
   <option value="60">60 et plus</option><option value="50">50 et plus</option></select>
  <label class="small"><input type="checkbox" id="pub"> secteur public seulement</label>
  <span class="compte" id="compte"></span>
 </div>
 <div class="scroll"><table>
  <thead><tr><th class="num">Score</th><th>Intitulé</th><th>Employeur</th><th>Famille</th>
   <th>Contrat</th><th class="num">Salaire</th><th class="num">km</th></tr></thead>
  <tbody id="corps">{lignes}</tbody>
 </table></div>
 <p class="small" style="margin-top:10px">Les salaires marqués comme fourchettes larges sont des
 estimations de marché par famille de métier lorsque l'annonce ne chiffre rien — c'est le cas le
 plus fréquent au Luxembourg.</p>
</section>

<section id="public">
 <h2><span class="num">4</span>{E(pu['titre'])}</h2>
 <p class="chapo">{E(pu['intro'])}</p>
 <div class="grille g2">{emp}</div>
 <h3>{E(pu['ateliers']['titre'])}</h3>
 <p>{E(pu['ateliers']['texte'])}</p>
 <div class="encadre warn"><p>{E(pu['ateliers']['attention'])}</p></div>
</section>

<section id="salaires">
 <h2><span class="num">5</span>{E(m['titre'])}</h2>
 <ul>{''.join(f'<li>{E(x)}</li>' for x in m['constats'])}</ul>
 <h3>Fourchettes de rémunération, brut annuel</h3>
 <div class="scroll"><table>
  <thead><tr><th>Famille de métier</th><th class="num">Débutant sur le poste</th>
   <th class="num">Confirmé</th><th class="num">Senior</th></tr></thead>
  <tbody>{grille}</tbody></table></div>
 <p class="small" style="margin-top:10px">Hors 13e mois, primes et chèques-repas, usuels dans la
 finance luxembourgeoise. Les montants de la fonction publique sont des ordres de grandeur.</p>
</section>

<section id="missions">
 <h2><span class="num">6</span>{E(mi['titre'])}</h2>
 <div class="encadre warm">
  <p><b>{E(mi['cadre']['titre'])}</b></p>
  <ul style="margin:8px 0 0">{''.join(f'<li>{E(x)}</li>' for x in mi['cadre']['points'])}</ul>
 </div>
 {opts}
 <h3>{E(mi['competences']['titre'])}</h3>
 <div class="scroll"><table>
  <thead><tr><th>Compétence</th><th>Durée</th><th>Où</th></tr></thead>
  <tbody>{comp}</tbody></table></div>
</section>

<section id="parler">
 <h2><span class="num">7</span>{E(co['titre'])}</h2>
 <ul>{''.join(f'<li>{E(x)}</li>' for x in co['principes'])}</ul>
 <h3>Les aménagements à demander, nommément</h3>
 <div class="carte"><ul style="margin:0">
  {''.join(f'<li>{E(x)}</li>' for x in co['amenagements'])}</ul></div>
</section>

<section id="consulter">
 <h2><span class="num">8</span>{E(cs['titre'])}</h2>
 <p class="chapo">{E(cs['intro'])}</p>

 <div class="encadre">
  <p><b>{E(cs['decouverte']['titre'])}</b></p>
  <p style="margin-top:8px">{E(cs['decouverte']['texte'])}</p>
  <ul class="liens">{liens_eu}</ul>
  <p class="small" style="margin-top:6px">{E(cs['decouverte']['astuce'])}</p>
 </div>

 <div class="scroll"><table>
  <thead><tr>{''.join(f'<th>{E(c)}</th>' for c in cs['colonnes'])}</tr></thead>
  <tbody>{src_lignes}</tbody>
 </table></div>
 <div class="encadre warm"><p>{E(cs['note'])}</p></div>
</section>

<section id="methode">
 <h2><span class="num">9</span>Méthode et sources</h2>
 <p>Les offres proviennent de jobs.lu, dépouillé le {date.today().strftime('%d/%m/%Y')} sur
 41 requêtes ciblées ; chaque annonce retenue a été téléchargée et lue en entier, puis notée par
 un script de scoring lexical dont les règles sont publiées avec ce dossier. Les signaux de marché
 (répartition CDI/CDD/intérim, part du télétravail) proviennent d'un relevé complémentaire de
 855 offres sur Moovijob. L'ADEM JobBoard exige une authentification et GovJobs est protégé par un
 captcha, et ne sont donc pas dans le classement. Une vérification a toutefois montré qu'une large
 part du vivier de l'ADEM est accessible anonymement via EURES, le portail européen de l'emploi —
 environ 3 600 postes luxembourgeois, texte intégral, sans compte : les recherches prêtes à l'emploi
 figurent à la section précédente.</p>
 <p class="small">Limites assumées : le score est calculé sur le texte des annonces, qui décrit ce
 que l'employeur veut montrer, pas la réalité sonore d'un plateau. Un score élevé signifie
 « à examiner », jamais « à accepter ». La question du nombre de personnes dans le bureau se pose
 en entretien, pas ici.</p>
 <h3>Sources</h3>
 <ul>{''.join(f'<li><a href="{E(s["url"])}" target="_blank" rel="noopener">{E(s["titre"])}</a></li>' for s in D['sources'])}</ul>
</section>

</main>

<footer class="wrap">
 <p>Page privée, non référencée. Généré le {date.today().strftime('%d/%m/%Y')} à partir de
 <code>data/dossier.json</code> et <code>data/offres_classees.json</code>.
 Pour rafraîchir : <code>python3 scripts/collecte_jobslu.py &amp;&amp; python3 scripts/score.py &amp;&amp; python3 scripts/build.py</code>.</p>
</footer>

<button class="theme" id="bt">clair / sombre</button>
<script>
(function(){{
 var q=document.getElementById('q'),f=document.getElementById('f'),c=document.getElementById('c'),
     s=document.getElementById('s'),pb=document.getElementById('pub'),
     corps=document.getElementById('corps'),cpt=document.getElementById('compte'),
     rows=[].slice.call(corps.rows);
 function maj(){{
  var t=q.value.toLowerCase().trim(),ff=f.value,cc=c.value,ss=+s.value,pp=pb.checked,n=0;
  rows.forEach(function(r){{
   var ok=(!t||r.dataset.t.indexOf(t)>-1)&&(!ff||r.dataset.f===ff)&&(!cc||r.dataset.c===cc)
        &&(+r.dataset.s>=ss)&&(!pp||r.dataset.p==='1');
   r.hidden=!ok; if(ok)n++;
  }});
  cpt.textContent=n+' offre'+(n>1?'s':'');
 }}
 [q,f,c,s,pb].forEach(function(e){{e.addEventListener('input',maj)}});
 maj();
 var bt=document.getElementById('bt');
 try{{var v=localStorage.getItem('th'); if(v)document.documentElement.dataset.theme=v;}}catch(e){{}}
 bt.addEventListener('click',function(){{
  var d=document.documentElement,
      cur=d.dataset.theme||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'),
      nv=cur==='dark'?'light':'dark';
  d.dataset.theme=nv; try{{localStorage.setItem('th',nv)}}catch(e){{}}
 }});
}})();
</script>
"""
    out = RACINE / "index.html"
    out.write_text(doc, encoding="utf-8")
    print(f"{out} ({len(doc)//1024} Ko, {len(OFFRES)} offres)")


if __name__ == "__main__":
    main()
