# SolarVillage — Dimensionnement PV hors-reseau pour villages enclave

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.36-FF4B4B?logo=streamlit&logoColor=white)
![Simulation](https://img.shields.io/badge/Simulation-8760h_vectorisee-FFB703)
![LPSP](https://img.shields.io/badge/Contrainte-LPSP_%E2%89%A4_5%25-success)

> **Master 2 Genie Informatique — Analyse Numerique et Applications**  
> Universite Nangui Abrogoua, Abidjan, Cote d'Ivoire — 2025–2026  
> Auteur : **Daouda Diallo**

---

## Le probleme

**600 millions d'Africains** n'ont pas acces a l'electricite. Les villages enclave
dependent de groupes electrogenes couteux et polluants. Le dimensionnement d'un
systeme solaire hors-reseau est complexe : trop petit = coupures, trop grand = gaspillage.

## La solution

SolarVillage calcule le couple optimal **(puissance crete PV, capacite batterie)**
qui garantit LPSP <= 5% au moindre cout, en simulant 8 760 heures d'operation et
en analysant la robustesse sur 200 scenarios climatiques Monte-Carlo.

---

## Demo rapide

```bash
git clone https://github.com/ton-username/SolarVillage.git
cd SolarVillage
pip install -r requirements.txt
streamlit run app.py
```

---

## Modules

| Page | Contenu |
|------|---------|
| **Ressource solaire** | Donnees NASA POWER, GHI mensuel, profil journalier, energie Simpson |
| **Profil de charge** | Foyers + ecole + dispensaire + pompe. Courbe de charge 8760h |
| **Simulation systeme** | 8760h vectorise NumPy. Modele 5 parametres LM. SOC batterie heure par heure |
| **Dimensionnement** | Grille (Np, Nb) + Nelder-Mead. Front de Pareto cout vs LPSP. Monte-Carlo IC 95% |

---

## Methodes d'analyse numerique implementees from scratch

| Methode | Fichier | Complexite / Role |
|---------|---------|------------------|
| **Simpson composee (ordre 4)** | `simpson.py` | O(h^4) — Energie journaliere |
| **Splines bicubiques 2D** | `splines_2d.py` | Interpolation grille NASA POWER |
| **Modele 5 parametres diode** | `pv_model.py` | Identification par LM |
| **Levenberg-Marquardt** | `pv_model.py` | Moindres carres non lineaires |
| **SPA solaire NREL simplifie** | `solar_position.py` | Position solaire horaire |
| **Grille exhaustive** | `grid_search.py` | O(n^2) — Exploration (Np, Nb) |
| **Nelder-Mead multi-start** | `refinement.py` | Raffinement local optimum |
| **Monte-Carlo parametrique** | `monte_carlo.py` | Robustesse interannuelle N=200 |

---

## Le modele PV a 5 parametres

```
I = Iph - I0*(exp((V + Rs*I)/(a*Vt)) - 1) - (V + Rs*I)/Rsh

Parametres identifies par Levenberg-Marquardt :
  Iph  : courant photogenere
  I0   : courant de saturation
  Rs   : resistance serie
  Rsh  : resistance shunt
  a    : facteur d'idealite
```

---

## Architecture

```
SolarVillage/
├── app.py                          # Landing page
├── pages/
│   ├── 1_Ressource_solaire.py
│   ├── 2_Profil_de_charge.py
│   ├── 3_Simulation_systeme.py
│   └── 4_Dimensionnement.py
├── solarvillage/
│   ├── geometry/      # solar_position (SPA NREL)
│   ├── physics/       # pv_model (5 params + LM), battery_model
│   ├── numerics/      # simpson, splines_2d
│   ├── data/          # nasa_power (API + cache), load_profiles
│   ├── simulation/    # hourly_simulator (8760h vectorise)
│   ├── optimization/  # grid_search, refinement (Nelder-Mead)
│   └── analysis/      # monte_carlo (N=200)
├── tests/             # pytest — 3 suites de tests
├── .streamlit/
│   └── config.toml    # Theme jaune sombre
└── requirements.txt
```

---

## Tests

```bash
pytest tests/ -v
```

| Suite | Ce qui est verifie |
|-------|--------------------|
| `test_solar_position.py` | Elevation Abidjan solstice ete dans [65, 85], nuit negative, symetrie |
| `test_simpson.py` | Exact sur polynomes degre 3, ordre 4 log-log, comparaison scipy |
| `test_battery_simulation.py` | LPSP=0 si surdimensionne, LPSP>0.3 si sous-dimensionne, SOC dans [SOC_min, 1] |

---

## Contexte academique

Projet realise dans le cadre du module **Analyse Numerique et Applications** du M2 GI,
encadre par le corps enseignant de l'UNA Abidjan. La simulation 8760h est entierement
vectorisee sous NumPy (< 0.1s). Toutes les methodes sont implementees from scratch,
y compris Simpson, les splines 2D et l'identification LM du modele PV.

---

*Daouda Diallo — daou.diall227@gmail.com*
