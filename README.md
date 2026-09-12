# SauvAK2026 — dossier emploi adapté, Luxembourg

Recherche d'un emploi réellement supportable au Luxembourg pour une personne autiste
(besoin d'un environnement calme, casque autorisé, faible luminosité, tâches à règles
explicites, management prévisible), et exploration d'une seconde voie : des revenus
propres hors contrat de travail.

Le livrable est **`index.html`** — une page statique, autonome, publiée en accès anonyme.

## Confidentialité

La page ne contient **aucun nom, aucune initiale, aucune adresse, aucun diagnostic
nominatif**. Elle est publiée sous un nom de dépôt non devinable et porte
`<meta name="robots" content="noindex,nofollow">` : accessible à qui a le lien,
invisible pour les moteurs de recherche. C'est une protection par obscurité, pas un
contrôle d'accès — ne pas diffuser le lien au-delà du cercle voulu.

## Structure

```
index.html                     la page publiée
data/dossier.json              contenu éditorial (droits, pistes, salaires, plan)
data/offres_brutes.json        offres collectées, descriptions complètes
data/offres_classees.json      offres notées et triées
scripts/collecte_jobslu.py     collecte jobs.lu (41 requêtes ciblées)
scripts/score.py               notation sur 5 axes, 100 points
scripts/build.py               génération de index.html
docs/SCORING.md                règles de notation, en clair
```

## Rafraîchir

```bash
python3 scripts/collecte_jobslu.py   # ~8 min, recharge les offres
python3 scripts/score.py             # renote et reclasse
python3 scripts/build.py             # régénère index.html
git commit -am "maj offres" && git push
```

Pour modifier le contenu rédactionnel sans recollecter : éditer `data/dossier.json`,
puis `python3 scripts/build.py`.

## Sources de données

| Source | Accès | Usage |
|---|---|---|
| jobs.lu | libre | collecte automatisée, annonces lues intégralement — base du classement |
| EURES (portail européen) | libre, sans compte | **reprend les offres déclarées à l'ADEM** : ≈ 3 600 postes au Luxembourg, texte intégral. Navigable par URL, non scriptable (l'API interne refuse les requêtes reconstruites). Liens de recherche prêts à l'emploi dans la page. |
| Moovijob | Cloudflare, navigateur uniquement | relevé ponctuel de 855 offres pour les signaux de marché |
| ADEM JobBoard | compte requis | **à consulter à la main** — c'est là que le statut de salarié handicapé rend le profil visible des employeurs sous quota |
| GovJobs | captcha (un clic dans un navigateur ordinaire) | **à consulter à la main** — postes de l'État et inscription à l'EAG |
| Indeed.lu, Monster.lu, Jooble | 403 pour un script | à couvrir par alerte e-mail |
| ADEM, Guichet.lu, fonction-publique.lu, EPSO, CCSS | libre | cadre juridique du statut de salarié handicapé et de l'activité indépendante |

La section « Où chercher soi-même » de la page détaille, pour chacune, quoi y faire et à quel
rythme. Les deux sources non automatisables sont aussi les moins fréquentées par les autres
candidats et ignorées des agrégateurs commerciaux : c'est une raison d'y aller, pas de les éviter.
