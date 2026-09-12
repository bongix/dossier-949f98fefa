# Règles de notation

Chaque offre est notée sur 100. Le score mesure la **supportabilité** d'un poste pour
ce profil — pas sa qualité, pas son salaire, pas son prestige. Un score de 85 veut dire
« à examiner sérieusement », jamais « à accepter ».

Le calcul est lexical : il s'applique au texte intégral de l'annonce (titre + employeur
+ description), normalisé sans accents et en minuscules. Voir `scripts/score.py`.

## Axe 1 — Environnement sensoriel (30 points)

Base 16, puis on ajoute les signaux de calme et on retranche les signaux de bruit.

Pénalisé : centre d'appels (−14), standard téléphonique (−10), restauration, chantier (−12),
accueil physique, réception, front desk (−8 à −9), magasin, entrepôt, ligne de production (−8 à −9),
open space (−5), déplacements fréquents (−6).

Bonifié : back-office (+12), archivage, saisie, data entry (+7 à +8), réconciliation (+8),
télétravail (+8), gestion documentaire (+7), indexation (+7).

## Axe 2 — Clarté des règles (25 points)

Base 10.

Bonifié : procédure, checklist, conformité, KYC/AML, réglementaire, contrôle, vérification,
souci du détail, rigueur, méthodique (+4 à +7 chacun).

Pénalisé : « fast-paced » (−8), « sous pression » (−8), multitâche (−7), rythme soutenu (−7),
priorités changeantes (−8), « porter plusieurs casquettes » (−8), polyvalence (−5).

## Axe 3 — Faible exposition sociale (20 points)

Base 14.

Pénalisé : prospection (−10), management d'équipe (−10), business development (−10),
commercial, vente, client facing (−8 à −9), réseautage (−7). Un intitulé contenant
manager / head of / director / responsable retire 8 points supplémentaires.

Bonifié : travail autonome (+6 à +7), concentration (+8), temps partiel (+6),
horaires flexibles (+5).

## Axe 4 — Adéquation au parcours (15 points)

Fonds, OPCVM, transfer agency, dépositaire, titres, banque, régulateur, CSSF, AMF,
comptabilité, administratif — et, côté création, graphisme, illustration, PAO, mise en page.

## Axe 5 — Praticité (10 points)

Distance depuis Sandweiler (6 pts à ≤ 10 km, 5 à ≤ 15, 3 à ≤ 25, 1 à ≤ 40, 0 au-delà),
type de contrat (+2 CDI, +1 CDD), temps partiel possible (+2), luxembourgeois ou allemand
courant exigé (−3), stage ou alternance (−3).

## Exclusions

Sont retirés du classement : les stages, alternances et contrats étudiants (intitulé ou
type de contrat), et tout poste à plus de 60 km de Sandweiler.

## Estimation salariale

Si l'annonce chiffre une rémunération, elle est reprise telle quelle (les montants mensuels
sont annualisés sur 13 mois, usage courant au Luxembourg). Sinon, la famille de métier est
détectée par expression régulière sur l'intitulé et le début de la description, et la
fourchette de marché correspondante est appliquée — voir la table `MARCHE` dans
`scripts/score.py`, construite à partir des guides de rémunération 2026 de la place.

## Ce que la notation ne peut pas voir

Le niveau sonore réel d'un plateau, le style du manager, la culture d'équipe, la tolérance
effective au port du casque. Une annonce décrit ce que l'employeur veut montrer. Ces
questions se posent en entretien — la liste figure dans la section « Comment en parler »
de la page.
