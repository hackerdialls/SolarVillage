"""SolarVillage — Landing page premium."""

import streamlit as st

st.set_page_config(
    page_title="SolarVillage · Dimensionnement PV Hors-Réseau",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
* { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

.hero {
    background: linear-gradient(135deg, #0A0A00 0%, #141200 40%, #1A1400 100%);
    padding: 80px 60px 60px;
    position: relative; overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute; top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(ellipse at 65% 45%, rgba(255,183,3,0.14) 0%, transparent 60%);
    animation: pulse 6s ease-in-out infinite;
}
@keyframes pulse { 0%,100%{opacity:.5} 50%{opacity:1} }

.badge {
    display: inline-block;
    background: rgba(255,183,3,0.12);
    border: 1px solid rgba(255,183,3,0.38);
    color: #FFB703;
    padding: 6px 16px; border-radius: 20px;
    font-size: 13px; font-weight: 600;
    letter-spacing: 1px; text-transform: uppercase;
    margin-bottom: 24px;
}
.hero-title {
    font-size: 72px; font-weight: 900; line-height: 1.05;
    background: linear-gradient(135deg, #FFFFFF 0%, #FFE57F 55%, #FFB703 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0 0 20px;
}
.hero-sub {
    font-size: 20px; color: rgba(255,251,240,0.68);
    max-width: 600px; line-height: 1.6; margin-bottom: 40px;
}
.hero-stats {
    display: flex; gap: 48px;
    margin-top: 48px; padding-top: 48px;
    border-top: 1px solid rgba(255,255,255,0.07);
}
.stat { text-align: left; }
.stat-num { font-size: 42px; font-weight: 800; color: #FFB703; line-height: 1; }
.stat-label { font-size: 13px; color: rgba(255,251,240,0.45); margin-top: 4px;
    text-transform: uppercase; letter-spacing: 0.5px; }

.cards-section { padding: 60px; background: #0A0A00; }
.section-title { font-size: 36px; font-weight: 700; color: #FFFBF0; margin-bottom: 8px; }
.section-sub { font-size: 16px; color: rgba(255,251,240,0.45); margin-bottom: 40px; }

.cards-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
.card {
    background: linear-gradient(145deg, #141200, #111000);
    border: 1px solid rgba(255,183,3,0.15);
    border-radius: 16px; padding: 28px;
    transition: all 0.3s ease; position: relative; overflow: hidden;
}
.card::after {
    content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #FFB703, #FFD60A);
    transform: scaleX(0); transition: transform 0.3s ease; transform-origin: left;
}
.card:hover { border-color: rgba(255,183,3,0.45); transform: translateY(-4px);
    box-shadow: 0 20px 40px rgba(255,183,3,0.12); }
.card:hover::after { transform: scaleX(1); }
.card-icon { font-size: 36px; margin-bottom: 16px; }
.card-title { font-size: 18px; font-weight: 700; color: #FFFBF0; margin-bottom: 8px; }
.card-desc { font-size: 14px; color: rgba(255,251,240,0.5); line-height: 1.6; }

/* Alert banner */
.alert-banner {
    background: linear-gradient(90deg, rgba(255,183,3,0.10), rgba(255,183,3,0.04));
    border-left: 4px solid #FFB703;
    padding: 20px 60px; margin: 0;
    display: flex; align-items: center; gap: 16px;
}
.alert-text { color: rgba(255,251,240,0.8); font-size: 15px; }
.alert-num { color: #FFB703; font-weight: 800; font-size: 20px; }

.methods-section {
    padding: 60px;
    background: linear-gradient(180deg, #141200 0%, #0A0A00 100%);
}
.method-tag {
    display: inline-block;
    background: rgba(255,183,3,0.10);
    border: 1px solid rgba(255,183,3,0.28);
    color: #FFD60A;
    padding: 8px 16px; border-radius: 8px;
    font-size: 13px; font-weight: 600; margin: 6px;
}

.footer {
    padding: 40px 60px; background: #060600;
    border-top: 1px solid rgba(255,255,255,0.05);
    display: flex; justify-content: space-between; align-items: center;
}
.footer-left { color: rgba(255,251,240,0.35); font-size: 14px; }
.footer-link { color: rgba(255,183,3,0.7); font-size: 14px; text-decoration: none; margin-left: 20px; }

.cta-row { display: flex; gap: 16px; margin-top: 16px; }
.cta-btn {
    background: linear-gradient(135deg, #D49000, #FFB703);
    color: #0A0A00; border: none; padding: 14px 32px;
    border-radius: 12px; font-size: 16px; font-weight: 700;
    cursor: pointer; box-shadow: 0 8px 24px rgba(255,183,3,0.35);
}
.cta-outline {
    background: transparent; border: 2px solid rgba(255,183,3,0.38);
    color: #FFB703; padding: 14px 32px;
    border-radius: 12px; font-size: 16px; font-weight: 600; cursor: pointer;
}
</style>

<!-- ALERT BANNER -->
<div class="alert-banner">
  <span style="font-size:24px">&#9889;</span>
  <div class="alert-text">
    <span class="alert-num">600 millions</span> d'Africains sans acces a l'electricite.
    SolarVillage dimensionne les micro-reseaux PV hors-reseau en
    <span class="alert-num">&lt; 1 seconde</span>.
  </div>
</div>

<!-- HERO -->
<div class="hero">
  <div class="badge">&#9728; Analyse Numerique · M2 Genie Informatique · UNA Abidjan</div>
  <h1 class="hero-title">SolarVillage</h1>
  <p class="hero-sub">
    Optimisation de systemes photovoltaiques hors-reseau par simulation numerique
    <strong style="color:#FFD60A">8 760 h vectorisee</strong>.
    Du modele a 5 parametres a la carte de risque Monte-Carlo en quelques clics.
  </p>
  <div class="cta-row">
    <span class="cta-btn">&#9728; Lancer la simulation</span>
    <span class="cta-outline">&#128208; Dimensionner un village</span>
  </div>
  <div class="hero-stats">
    <div class="stat">
      <div class="stat-num">8 760h</div>
      <div class="stat-label">Simulation annuelle</div>
    </div>
    <div class="stat">
      <div class="stat-num">O(n&sup2;)</div>
      <div class="stat-label">Grille d'optimisation</div>
    </div>
    <div class="stat">
      <div class="stat-num">200</div>
      <div class="stat-label">Trajectoires Monte-Carlo</div>
    </div>
    <div class="stat">
      <div class="stat-num">5 params</div>
      <div class="stat-label">Modele diode PV</div>
    </div>
  </div>
</div>

<!-- PAGES -->
<div class="cards-section">
  <div class="section-title">Modules de la plateforme</div>
  <div class="section-sub">4 pages interactives — du gisement solaire a l'optimisation du micro-reseau</div>
  <div class="cards-grid">
    <div class="card">
      <div class="card-icon">&#128202;</div>
      <div class="card-title">Tableau de bord</div>
      <div class="card-desc">Gisement solaire NASA POWER, profil de charge quotidien, KPIs systeme en temps reel.</div>
    </div>
    <div class="card">
      <div class="card-icon">&#9728;</div>
      <div class="card-title">Simulation PV</div>
      <div class="card-desc">8 760h vectorise NumPy. Modele 5 parametres LM. Bilan SOC batterie heure par heure.</div>
    </div>
    <div class="card">
      <div class="card-icon">&#128208;</div>
      <div class="card-title">Dimensionnement</div>
      <div class="card-desc">Grille (Np, Nb) + Nelder-Mead. Front de Pareto cout vs LPSP. Optimum garanti.</div>
    </div>
    <div class="card">
      <div class="card-icon">&#127922;</div>
      <div class="card-title">Robustesse Monte-Carlo</div>
      <div class="card-desc">200 scenarios d'irradiance. Distribution LPSP, P(LPSP &le; 5%), intervalles de confiance 95%.</div>
    </div>
  </div>
</div>

<!-- METHODES -->
<div class="methods-section">
  <div class="section-title">Methodes d'analyse numerique</div>
  <div class="section-sub">Implementees from scratch &middot; validees scientifiquement &middot; documentees</div>
  <div style="margin-top: 24px;">
    <span class="method-tag">Modele 5 parametres diode</span>
    <span class="method-tag">Levenberg-Marquardt LM</span>
    <span class="method-tag">Simpson composee O(h&#8308;)</span>
    <span class="method-tag">Splines bicubiques 2D</span>
    <span class="method-tag">SPA solaire NREL simplifie</span>
    <span class="method-tag">Nelder-Mead multi-start</span>
    <span class="method-tag">Monte-Carlo parametrique</span>
    <span class="method-tag">Simulation 8 760h vectorisee</span>
  </div>
</div>

<!-- FOOTER -->
<div class="footer">
  <div class="footer-left">
    <strong style="color:#FFB703">SolarVillage</strong> &middot; Daouda Diallo &middot; M2 GI, Universite Nangui Abrogoua &middot; 2025&ndash;2026
  </div>
  <div class="footer-right">
    <span class="footer-link">GitHub</span>
    <span class="footer-link">LinkedIn</span>
    <span class="footer-link">NASA POWER</span>
  </div>
</div>
""", unsafe_allow_html=True)
