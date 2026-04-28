# SolarVillage — Spécification d'implémentation pour Claude Code

> **Objectif de ce document** : servir de spécification complète et auto-suffisante pour implémenter le projet **SolarVillage** avec **Streamlit**. Ce document doit être lu intégralement par Claude Code avant tout codage.

---

## 0. Contexte du projet

**Pour qui** : étudiant en M2 Génie Informatique à l'Université Nangui Abrogoua (Abidjan, Côte d'Ivoire), projet du module d'analyse numérique. Cible utilisateur final : ONG d'électrification rurale (Energy 4 Impact, Practical Action), bureaux d'études, bailleurs (Banque Mondiale, BAD).

**Pourquoi** : plus de 600 millions d'Africains n'ont pas accès à l'électricité. Le solaire off-grid est la solution, mais le dimensionnement reste empirique : surdimensionner coûte cher, sous-dimensionner crée des coupures. SolarVillage calcule le couple optimal (puissance crête, capacité batterie).

**Quoi** : une application **Streamlit** qui :
1. Récupère l'irradiance solaire au point GPS du village (NASA POWER).
2. Modélise la production photovoltaïque horaire sur 8760 heures (1 année type).
3. Modélise la consommation (foyer, école, dispensaire, pompage).
4. Optimise le couple (Pcrête, Cbatterie) sous contrainte de fiabilité (LPSP).
5. Génère un rapport technique de dimensionnement.

**Périmètre académique** : démonstration explicite des méthodes d'analyse numérique (splines bicubiques 2D, intégration de Simpson, optimisation Nelder-Mead, Monte-Carlo, moindres carrés non linéaires).

---

## 1. Stack technique

### Dépendances obligatoires

```txt
# requirements.txt
streamlit>=1.36
numpy>=1.26
scipy>=1.12
pandas>=2.2
plotly>=5.20
matplotlib>=3.8
requests>=2.31
pydantic>=2.6
python-dotenv>=1.0
```

### Dépendances optionnelles

```txt
folium>=0.16          # carte du village
streamlit-folium>=0.20
SALib>=1.5            # analyse de sensibilité Morris
pytest>=8.1
fpdf2>=2.7            # génération du rapport PDF de dimensionnement
```

### Contraintes d'environnement

- **OS cible** : Windows.
- **Python** : 3.11 ou 3.12.
- **Pas de toolchain native**.
- **Pas de pvlib** : on réimplémente la position du soleil et le modèle PV pour démontrer les méthodes au prof. pvlib peut servir de référence pour les tests.

---

## 2. Architecture des fichiers

```
solarvillage/
├── app.py                      # entrypoint Streamlit
├── requirements.txt
├── .env.example                # NASA_POWER_API, etc.
├── README.md
│
├── pages/
│   ├── 1_📍_Localisation.py
│   ├── 2_☀️_Ressource_solaire.py
│   ├── 3_🔌_Profil_de_charge.py
│   ├── 4_⚙️_Simulation_systeme.py
│   ├── 5_🎯_Dimensionnement.py
│   └── 6_📄_Rapport.py
│
├── solarvillage/               # package métier
│   ├── __init__.py
│   ├── config.py               # constantes physiques, prix par défaut
│   ├── geometry/
│   │   ├── __init__.py
│   │   └── solar_position.py   # algorithme NREL SPA simplifié
│   ├── physics/
│   │   ├── __init__.py
│   │   ├── pv_model.py         # modèle 5 paramètres (single diode)
│   │   ├── battery_model.py    # bilan d'énergie + état de charge
│   │   └── irradiance.py       # composition GHI/DNI/DHI, modèle Liu-Jordan
│   ├── numerics/
│   │   ├── __init__.py
│   │   ├── splines_2d.py       # interpolation bicubique
│   │   ├── simpson.py          # Simpson composée
│   │   ├── nelder_mead.py      # implémentation from scratch (option)
│   │   └── least_squares.py    # moindres carrés non linéaires
│   ├── data/
│   │   ├── __init__.py
│   │   ├── nasa_power.py       # client API + cache
│   │   └── load_profiles.py    # profils de consommation types
│   ├── simulation/
│   │   ├── __init__.py
│   │   └── hourly_simulator.py # CŒUR : simulation 8760 h
│   ├── optimization/
│   │   ├── __init__.py
│   │   ├── grid_search.py
│   │   ├── refinement.py       # Nelder-Mead autour du minimum
│   │   └── pareto.py           # front de Pareto coût/fiabilité
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── monte_carlo.py
│   │   └── morris.py           # analyse de sensibilité Morris (SALib)
│   └── reporting/
│       ├── __init__.py
│       └── pdf_report.py
│
├── data/
│   ├── cache/                  # cache NASA POWER
│   ├── load_profiles/          # CSVs de profils typiques
│   └── pv_panels/              # fiches techniques constructeurs
│
└── tests/
    ├── test_solar_position.py
    ├── test_pv_model.py        # validation contre fiche technique
    ├── test_simpson.py
    ├── test_splines_2d.py
    ├── test_battery_simulation.py
    └── test_optimization_synthetic.py
```

**Règle d'or** : aucune dépendance de `solarvillage/` à `streamlit`. Le package est utilisable en notebook ou en script CLI.

---

## 3. Cœur mathématique

### 3.1 Position du soleil (NREL SPA simplifié)

Implémenter dans `geometry/solar_position.py` une version simplifiée précise au degré (suffisante pour le dimensionnement). Les formules clés :

```
δ (déclinaison) = 23.45° * sin(360° * (284 + n) / 365)
ω (angle horaire) = 15° * (heure_solaire - 12)
sin(α) = sin(φ) sin(δ) + cos(φ) cos(δ) cos(ω)   # élévation solaire
cos(γ) = (sin(α) sin(φ) - sin(δ)) / (cos(α) cos(φ))   # azimut
```

avec n = jour de l'année, φ = latitude.

### 3.2 Modèle PV à 5 paramètres (single diode)

Équation du modèle à diode unique :

```
I = I_L - I_0 * (exp((V + I*R_s) / (n*Vt)) - 1) - (V + I*R_s) / R_sh
```

5 paramètres à identifier (I_L, I_0, R_s, R_sh, n) à partir des données STC de la fiche technique du panneau (Vmp, Imp, Voc, Isc, NOCT). Méthode : **moindres carrés non linéaires** (Levenberg-Marquardt via `scipy.optimize.least_squares`).

C'est une **application directe** des moindres carrés non linéaires.

### 3.3 Désagrégation horaire (modèle Liu-Jordan)

NASA POWER fournit l'irradiance journalière (kWh/m²/jour) ou horaire (W/m²) selon l'endpoint. Si seulement le journalier est disponible, on désagrège :

```
r_t = (π/24) * (a + b*cos(ω)) * (cos(ω) - cos(ω_s)) / (sin(ω_s) - ω_s*cos(ω_s))
GHI(t) = r_t * GHI_journalier
```

Puis interpolation **splines cubiques** pour obtenir un profil lisse à 1 minute si besoin.

### 3.4 Interpolation bicubique 2D (NASA POWER)

Pour passer de la grille NASA POWER (0.5° × 0.5°) au point GPS exact du village :

Implémenter `numerics/splines_2d.py` à partir de `scipy.interpolate.RectBivariateSpline` (`kx=3, ky=3`). Wrapper avec docstring expliquant la méthode pour le rapport.

### 3.5 Énergie produite : intégration de Simpson composée

Sur chaque journée :

```
E_jour = ∫₀²⁴ P_panneau(t) dt
```

Implémenter `numerics/simpson.py` from scratch. Comparer à `scipy.integrate.simpson` pour validation. **Le Simpson maison est ce qu'on présente.**

```
fonction simpson_composee(y, h):
    n = len(y) - 1
    si n est impair: erreur
    S = y[0] + y[n]
    pour i de 1 à n-1:
        si i pair: S += 2 * y[i]
        sinon:     S += 4 * y[i]
    retourner S * h / 3
```

### 3.6 Simulation horaire du système (cœur de boucle)

Pseudocode `simulation/hourly_simulator.py` :

```
fonction simuler_systeme(P_crete, C_batterie, irradiance_8760, charge_8760, params):
    SOC ← C_batterie * 0.5    # état de charge initial 50%
    LPS ← 0                   # Loss of Power Supply (kWh)
    energies = {production: 0, consommation: 0, batterie_in: 0, batterie_out: 0, defaut: 0}

    pour h de 0 à 8759:
        P_pv = P_crete * irradiance[h] / 1000 * facteur_temperature(temp[h])
        P_charge = charge[h]
        delta = P_pv - P_charge

        si delta > 0:   # surplus → charger batterie
            charge_possible = min(delta, (C_batterie - SOC) / dt) / rendement_charge
            SOC += charge_possible * dt * rendement_charge
        sinon:          # déficit → décharger batterie
            decharge_demandee = -delta
            decharge_possible = min(decharge_demandee, SOC / dt) * rendement_decharge
            SOC -= decharge_possible * dt / rendement_decharge
            si decharge_possible < decharge_demandee:
                LPS += (decharge_demandee - decharge_possible) * dt

        # contraintes physiques
        SOC = clamp(SOC, SOC_min, C_batterie)

    LPSP = LPS / total_consommation
    retourner LPSP, energies
```

### 3.7 Optimisation (Pcrête, Cbatterie)

Stratégie en deux temps (`optimization/`) :

1. **Recherche par grille** sur (P_crete, C_batterie) ∈ [Pmin, Pmax] × [Cmin, Cmax].
   Évaluer LPSP et coût pour chaque combinaison.
   Filtrer les solutions vérifiant LPSP ≤ ε.
   Identifier la solution de coût minimal.

2. **Raffinement Nelder-Mead** autour de l'optimum de la grille (utiliser `scipy.optimize.minimize(method='Nelder-Mead')`).

3. **Variante avancée** : tracer le **front de Pareto** coût vs LPSP en faisant varier ε. Permet aux décideurs de choisir leur compromis.

### 3.8 Validation Monte-Carlo

`analysis/monte_carlo.py` : pour le dimensionnement optimal trouvé, lancer N = 1000 simulations en perturbant l'irradiance horaire (bruit gaussien sur valeurs journalières, σ = 15 % par exemple). Calculer la distribution de LPSP. Vérifier que P(LPSP ≤ ε) ≥ 95 %.

### 3.9 Validation obligatoire (tests scientifiques)

- **Test 1** : position du soleil à midi solaire un 21 juin à Abidjan : élévation ≈ 90° − |latitude − 23.45°|. Tolérance 0.5°.
- **Test 2** : ordre Simpson = 4 sur f(x) = sin(x) (régression log-log).
- **Test 3** : modèle PV à STC retourne Pmax = Pmpp (fiche technique) à 1 % près.
- **Test 4** : conservation d'énergie sur la simulation : `E_pv = E_consommée + E_perdue + ΔSOC + LPS`.
- **Test 5** : optimisation sur cas synthétique avec optimum connu (LPSP = 0 garanti par dimensionnement large).

---

## 4. UI Streamlit

### 4.1 Page d'accueil `app.py`

```python
import streamlit as st

st.set_page_config(
    page_title="SolarVillage",
    page_icon="☀️",
    layout="wide",
)

st.title("☀️ SolarVillage")
st.subheader("Dimensionnement optimal de systèmes solaires pour villages enclavés")

# présentation rapide + 6 cartes vers les pages
```

### 4.2 Page Localisation

- Carte folium centrée sur l'Afrique de l'Ouest.
- Clic sur la carte → récupère lat/lon.
- Champs latitude / longitude éditables.
- Bouton « Récupérer les données solaires » → appelle NASA POWER et met en cache.
- Affichage : altitude, fuseau horaire, durée moyenne d'ensoleillement.

### 4.3 Page Ressource solaire

- Affichage GHI moyen mensuel (graphe en barres).
- Profil journalier moyen pour le mois sélectionné (heatmap heure × mois).
- Onglet « Variabilité » : écart-type interannuel.
- Onglet « Analyse numérique » : courbe d'irradiance horaire interpolée par splines, intégrale journalière par Simpson et trapèzes (comparaison).

### 4.4 Page Profil de charge

Sidebar :
- Type de village : foyer simple / village complet (école + dispensaire) / pompage.
- Nombre de foyers.
- Présence d'une école (oui/non).
- Présence d'un dispensaire (oui/non).
- Pompage (oui/non, débit, hauteur manométrique).

Affichage :
- Profil journalier type (24 h).
- Consommation hebdomadaire et annuelle.
- Pic de demande (kW).

### 4.5 Page Simulation système

- Sliders : P_crete (kWc), C_batterie (kWh), efficacité onduleur, rendements batterie.
- Bouton « Simuler 1 an ».
- Résultats :
  - Onglet 1 : courbes annuelles (production, consommation, SOC).
  - Onglet 2 : statistiques (LPSP, autonomie moyenne, taux de couverture solaire).
  - Onglet 3 : journée critique (jour où LPS est maximale).
  - Onglet 4 : bilan énergétique annuel (Sankey diagram).

### 4.6 Page Dimensionnement (cœur de l'outil)

- Contraintes : LPSP_max (slider 1 % à 10 %), budget max (optionnel).
- Bouton « Dimensionner ».
- Sortie :
  - Solution optimale : P_crete, C_batterie, coût total.
  - Front de Pareto interactif (Plotly).
  - Tableau comparatif avec 3 alternatives (économique, équilibrée, premium).
  - Heatmap LPSP sur la grille (Pcrête, Cbatterie).
  - **Onglet « Robustesse »** : résultats Monte-Carlo (distribution LPSP).
  - **Onglet « Sensibilité »** : indices Morris hiérarchisés.

### 4.7 Page Rapport

- Bouton « Générer rapport PDF » (`reporting/pdf_report.py` avec fpdf2).
- Le PDF contient : page de garde, résumé exécutif, ressource solaire, profil de charge, dimensionnement retenu, bilan annuel, annexes techniques.

---

## 5. Phases d'implémentation (mappées sur les livrables)

> Claude Code doit implémenter dans cet ordre. Une phase ne démarre que si la précédente passe ses tests.

### Phase 1 — Modélisation physique (2 semaines)

**Livrables** :
- L1.1 : `geometry/solar_position.py` + `tests/test_solar_position.py`.
- L1.2 : `physics/pv_model.py` (modèle 5 paramètres) + `tests/test_pv_model.py`.
- L1.3 : `physics/battery_model.py`.
- L1.4 : `physics/irradiance.py` (Liu-Jordan, composition GHI/DNI/DHI).

**Critère** : tous les tests Phase 1 passent.

### Phase 2 — Données et interpolation (2 semaines)

**Livrables** :
- L2.1 : `data/nasa_power.py` avec cache local (parquet).
- L2.2 : `numerics/splines_2d.py` + `tests/test_splines_2d.py`.
- L2.3 : `numerics/simpson.py` + `tests/test_simpson.py` (vérifier ordre 4).
- L2.4 : `data/load_profiles.py` avec 4 profils types (foyer, école, dispensaire, pompage).

**Critère** : NASA POWER fonctionne pour Abidjan (5.36, -4.0) et donne des valeurs cohérentes (5–6 kWh/m²/jour).

### Phase 3 — Simulation et optimisation (2 semaines)

**Livrables** :
- L3.1 : `simulation/hourly_simulator.py` + `tests/test_battery_simulation.py`.
- L3.2 : `optimization/grid_search.py`.
- L3.3 : `optimization/refinement.py` (wrapper Nelder-Mead).
- L3.4 : `optimization/pareto.py`.
- L3.5 : `tests/test_optimization_synthetic.py`.

**Critère** : sur cas synthétique avec optimum connu, l'algo retrouve l'optimum à 5 % près.

### Phase 4 — Analyse de sensibilité et robustesse (1 semaine)

**Livrables** :
- L4.1 : `analysis/monte_carlo.py`.
- L4.2 : `analysis/morris.py` via SALib.

**Critère** : analyse Morris produit un classement cohérent des paramètres (irradiance > rendement > coût > ...).

### Phase 5 — UI Streamlit (3 semaines)

**Livrables** :
- L5.1 : `app.py` + page d'accueil.
- L5.2 : `pages/1_📍_Localisation.py` avec folium.
- L5.3 : `pages/2_☀️_Ressource_solaire.py`.
- L5.4 : `pages/3_🔌_Profil_de_charge.py`.
- L5.5 : `pages/4_⚙️_Simulation_systeme.py`.
- L5.6 : `pages/5_🎯_Dimensionnement.py` (cœur démo).
- L5.7 : `pages/6_📄_Rapport.py` avec génération PDF.

**Critère** : `streamlit run app.py` démarre, les 6 pages fonctionnent, génération de rapport PDF en moins de 10 s.

### Phase 6 — Étude de cas et soutenance (2 semaines)

- L6.1 : Étude de cas réelle sur 1 village ivoirien (par exemple un village proche de Bouaflé).
- L6.2 : Notebook `notebooks/etude_de_cas.ipynb` reproductible.
- L6.3 : Captures d'écran et démo dans `docs/`.
- L6.4 : Section README détaillant les méthodes d'analyse numérique utilisées.

---

## 6. Tests

```python
# tests/test_solar_position.py
from datetime import datetime
from solarvillage.geometry.solar_position import elevation_solaire

def test_midi_solaire_solstice_ete_abidjan():
    """Au midi solaire d'un 21 juin à Abidjan (lat 5.36°),
    l'élévation solaire doit être proche de 90° - |5.36° - 23.45°| ≈ 71.9°."""
    lat = 5.36
    lon = -4.0
    dt = datetime(2024, 6, 21, 12, 0, 0)  # midi local approximatif
    elev = elevation_solaire(lat, lon, dt)
    assert 71 < elev < 73, f"Elevation attendue ≈ 71.9°, observée {elev:.2f}°"

# tests/test_simpson.py
import numpy as np
from solarvillage.numerics.simpson import simpson_composee

def test_ordre_4_sur_sinus():
    """L'erreur de Simpson composée doit décroître en O(h^4)."""
    erreurs = []
    pas = []
    for n in [10, 20, 40, 80, 160]:
        x = np.linspace(0, np.pi, n + 1)
        y = np.sin(x)
        I = simpson_composee(y, np.pi / n)
        erreurs.append(abs(I - 2.0))
        pas.append(np.pi / n)
    ordre = np.polyfit(np.log(pas), np.log(erreurs), 1)[0]
    assert 3.8 < ordre < 4.2, f"Ordre Simpson attendu ≈ 4, observé {ordre:.2f}"

# tests/test_pv_model.py
def test_pmax_a_stc():
    """À conditions STC (1000 W/m², 25°C), le panneau doit produire
    Pmax = Pmpp de la fiche technique à 1% près."""
    ...
```

---

## 7. Conventions de code

Identiques aux deux autres projets :
- Commentaires et docstrings en **français**.
- Type hints partout.
- Format Google pour docstrings avec section `References`.
- Pas de `print` dans le code métier.
- Format `black`, 88 colonnes.

---

## 8. Critères d'acceptation finaux

- [ ] `pytest` tout vert (au moins 15 tests).
- [ ] Test ordre Simpson = 4 (log-log).
- [ ] Test position du soleil à 0.5° près.
- [ ] Test modèle PV à STC à 1 % près.
- [ ] `streamlit run app.py` lance les 6 pages sans erreur.
- [ ] Dimensionnement complet (de la saisie GPS au PDF) en < 30 s.
- [ ] Étude de cas village ivoirien documentée.
- [ ] Le README explique chaque méthode d'analyse numérique avec référence au cours.
- [ ] Le PDF de dimensionnement a une qualité « livrable ONG ».

---

## 9. Démarrage rapide pour Claude Code

```bash
pip install -r requirements.txt

# Phase 1 : physique
pytest tests/test_solar_position.py tests/test_pv_model.py -v

# Phase 2 : données + numérique
pytest tests/test_simpson.py tests/test_splines_2d.py -v

# Phase 3 : simulation
pytest tests/test_battery_simulation.py tests/test_optimization_synthetic.py -v

# Phase 5 : UI
streamlit run app.py
```

**Première commande à donner à Claude Code** :

> « Implémente la Phase 1 de SolarVillage en suivant `03_SolarVillage_SPEC.md`. Crée d'abord l'arborescence, puis `geometry/solar_position.py` (NREL SPA simplifié), puis `physics/pv_model.py` (modèle 5 paramètres ajustés par moindres carrés non linéaires sur les données STC), puis `physics/battery_model.py`. Termine par les tests `test_solar_position.py` et `test_pv_model.py` qui doivent passer. Ne commence pas la Phase 2 tant que tous les tests Phase 1 ne sont pas verts. »

---

## 10. Pièges connus à éviter

1. **NASA POWER quota** : 1000 requêtes/jour environ. Toujours mettre en cache (parquet local). Ne pas appeler l'API depuis Streamlit sans cache `@st.cache_data(ttl=86400)`.
2. **Fuseaux horaires** : NASA POWER renvoie des dates en UTC. Convertir en heure locale du village avant de tracer.
3. **Modèle PV : 5 paramètres mal posés** : le système est mal conditionné si on n'a que les valeurs STC. Utiliser des contraintes physiques (R_s ∈ [0, 5 Ω], n ∈ [1, 2]) et plusieurs points de départ.
4. **Simulation 8760 heures lente** : vectoriser avec NumPy. Une simulation pure Python avec boucle for prendra 10 s ; vectorisée elle prend < 0.1 s. C'est essentiel pour l'optimisation par grille (qui appelle la simulation 100 à 10 000 fois).
5. **Streamlit + cache** : la fonction `simuler_systeme` doit être décorée `@st.cache_data` avec une clé incluant tous les paramètres pour éviter les recalculs inutiles.
6. **Encodage Windows** : toujours `encoding='utf-8'` explicite.
7. **Optimum global vs local** : Nelder-Mead seul tombe dans des minima locaux. Toujours faire la grille **avant** le raffinement.
8. **fpdf2 et accents** : utiliser `pdf.set_font('Helvetica', '', 12)` et encoder en latin-1 ou utiliser une police TTF Unicode (DejaVu Sans).

---

## 11. Glossaire technique

| Terme | Définition |
|-------|-----------|
| **GHI** | Global Horizontal Irradiance, irradiance globale sur surface horizontale (W/m²) |
| **DNI** | Direct Normal Irradiance, irradiance directe normale au rayonnement (W/m²) |
| **DHI** | Diffuse Horizontal Irradiance, irradiance diffuse sur surface horizontale (W/m²) |
| **STC** | Standard Test Conditions : 1000 W/m², 25°C, AM 1.5 |
| **NOCT** | Nominal Operating Cell Temperature, température nominale de fonctionnement |
| **LPSP** | Loss of Power Supply Probability, probabilité de défaut de fourniture |
| **SOC** | State of Charge, état de charge de la batterie (kWh ou %) |
| **kWc** | kilowatt-crête, puissance nominale du panneau en STC |
| **MPPT** | Maximum Power Point Tracking, suivi du point de puissance maximum |
| **NREL SPA** | Solar Position Algorithm de la National Renewable Energy Laboratory |

---

*Fin de la spécification SolarVillage. Document destiné à Claude Code, à conserver dans la racine du projet.*
