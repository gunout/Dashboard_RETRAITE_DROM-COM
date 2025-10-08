

# dashboard_retraites_drom_com.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import random
import warnings
from functools import lru_cache
warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Retraites - DROM-COM",
    page_icon="👴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(45deg, #0055A4, #EF4135, #FFD700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .live-badge {
        background: linear-gradient(45deg, #0055A4, #00A3E0);
        color: white;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #0055A4;
        margin: 0.5rem 0;
    }
    .section-header {
        color: #0055A4;
        border-bottom: 2px solid #EF4135;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    .category-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 5px solid #0055A4;
        background-color: #f8f9fa;
    }
    .pension-change {
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
        font-size: 0.9rem;
        font-weight: bold;
    }
    .positive { background-color: #d4edda; border-left: 4px solid #28a745; color: #155724; }
    .negative { background-color: #f8d7da; border-left: 4px solid #dc3545; color: #721c24; }
    .neutral { background-color: #e2e3e5; border-left: 4px solid #6c757d; color: #383d41; }
    .category-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .territory-flag {
        padding: 0.5rem 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
        color: white;
    }
    .reunion-flag { background: linear-gradient(90deg, #0055A4 33%, #EF4135 33%, #EF4135 66%, #FFFFFF 66%); }
    .guadeloupe-flag { background: linear-gradient(90deg, #ED2939 50%, #002395 50%); }
    .martinique-flag { background: linear-gradient(90deg, #009739 33%, #002395 33%, #002395 66%, #FCD116 66%); }
    .guyane-flag { background: linear-gradient(90deg, #009739 50%, #FCD116 50%); }
    .mayotte-flag { background: linear-gradient(90deg, #FFFFFF 25%, #ED2939 25%, #ED2939 50%, #002395 50%, #002395 75%, #FCD116 75%); }
    .spierre-flag { background: linear-gradient(90deg, #002395 33%, #FFFFFF 33%, #FFFFFF 66%, #ED2939 66%); }
    .stbarth-flag { background: linear-gradient(90deg, #FFFFFF 50%, #FCD116 50%); }
    .stmartin-flag { background: linear-gradient(90deg, #ED2939 50%, #002395 50%); }
    .wallis-flag { background: linear-gradient(90deg, #ED2939 33%, #002395 33%, #002395 66%, #FCD116 66%); }
    .polynesie-flag { background: linear-gradient(90deg, #ED2939 25%, #FFFFFF 25%, #FFFFFF 50%, #FCD116 50%, #FCD116 75%, #002395 75%); }
    .caledonie-flag { background: linear-gradient(90deg, #002395 33%, #FCD116 33%, #FCD116 66%, #ED2939 66%); }
    .territory-selector {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #0055A4;
        margin-bottom: 1rem;
    }
    .loading-spinner {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 200px;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation de l'état de session
if 'territories_data' not in st.session_state:
    st.session_state.territories_data = {}
if 'selected_territory' not in st.session_state:
    st.session_state.selected_territory = 'REUNION'
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

# Fonctions globales avec cache pour éviter les problèmes de hashage
@st.cache_data(ttl=3600)
def get_territories_definitions():
    """Définit les territoires DROM-COM"""
    return {
        'REUNION': {
            'nom_complet': 'La Réunion',
            'type': 'DROM',
            'population': 860000,
            'superficie': 2511,
            'pib': 19.8,
            'drapeau': 'reunion-flag',
            'monnaie': 'EUR',
            'retraites_actif': True,
            'nombre_retraites': 180000,
            'montant_moyen_retraite': 1250
        },
        'GUADELOUPE': {
            'nom_complet': 'Guadeloupe',
            'type': 'DROM',
            'population': 384000,
            'superficie': 1628,
            'pib': 9.1,
            'drapeau': 'guadeloupe-flag',
            'monnaie': 'EUR',
            'retraites_actif': True,
            'nombre_retraites': 85000,
            'montant_moyen_retraite': 1180
        },
        'MARTINIQUE': {
            'nom_complet': 'Martinique',
            'type': 'DROM',
            'population': 376000,
            'superficie': 1128,
            'pib': 8.9,
            'drapeau': 'martinique-flag',
            'monnaie': 'EUR',
            'retraites_actif': True,
            'nombre_retraites': 82000,
            'montant_moyen_retraite': 1200
        },
        'GUYANE': {
            'nom_complet': 'Guyane',
            'type': 'DROM',
            'population': 290000,
            'superficie': 83534,
            'pib': 4.8,
            'drapeau': 'guyane-flag',
            'monnaie': 'EUR',
            'retraites_actif': True,
            'nombre_retraites': 45000,
            'montant_moyen_retraite': 1150
        },
        'MAYOTTE': {
            'nom_complet': 'Mayotte',
            'type': 'DROM',
            'population': 270000,
            'superficie': 374,
            'pib': 2.4,
            'drapeau': 'mayotte-flag',
            'monnaie': 'EUR',
            'retraites_actif': True,
            'nombre_retraites': 28000,
            'montant_moyen_retraite': 950
        },
        'STPIERRE': {
            'nom_complet': 'Saint-Pierre-et-Miquelon',
            'type': 'COM',
            'population': 6000,
            'superficie': 242,
            'pib': 0.2,
            'drapeau': 'spierre-flag',
            'monnaie': 'EUR',
            'retraites_actif': True,
            'nombre_retraites': 1500,
            'montant_moyen_retraite': 1350
        },
        'STBARTH': {
            'nom_complet': 'Saint-Barthélemy',
            'type': 'COM',
            'population': 10000,
            'superficie': 21,
            'pib': 0.6,
            'drapeau': 'stbarth-flag',
            'monnaie': 'EUR',
            'retraites_actif': True,
            'nombre_retraites': 2200,
            'montant_moyen_retraite': 1650
        },
        'STMARTIN': {
            'nom_complet': 'Saint-Martin',
            'type': 'COM',
            'population': 32000,
            'superficie': 54,
            'pib': 0.9,
            'drapeau': 'stmartin-flag',
            'monnaie': 'EUR',
            'retraites_actif': True,
            'nombre_retraites': 6500,
            'montant_moyen_retraite': 1400
        },
        'WALLIS': {
            'nom_complet': 'Wallis-et-Futuna',
            'type': 'COM',
            'population': 11500,
            'superficie': 142,
            'pib': 0.2,
            'drapeau': 'wallis-flag',
            'monnaie': 'XPF',
            'retraites_actif': True,
            'nombre_retraites': 1800,
            'montant_moyen_retraite': 950
        },
        'POLYNESIE': {
            'nom_complet': 'Polynésie française',
            'type': 'COM',
            'population': 280000,
            'superficie': 4167,
            'pib': 7.2,
            'drapeau': 'polynesie-flag',
            'monnaie': 'XPF',
            'retraites_actif': True,
            'nombre_retraites': 52000,
            'montant_moyen_retraite': 1100
        },
        'CALEDONIE': {
            'nom_complet': 'Nouvelle-Calédonie',
            'type': 'COM',
            'population': 271000,
            'superficie': 18575,
            'pib': 9.7,
            'drapeau': 'caledonie-flag',
            'monnaie': 'XPF',
            'retraites_actif': True,
            'nombre_retraites': 48000,
            'montant_moyen_retraite': 1250
        }
    }

@st.cache_data(ttl=3600)
def get_categories_retraites(territory_code):
    """Définit les catégories de retraites pour un territoire donné"""
    # Facteurs d'ajustement selon le territoire
    territory_factor = {
        'REUNION': 1.0,
        'GUADELOUPE': 0.95,
        'MARTINIQUE': 0.9,
        'GUYANE': 0.7,
        'MAYOTTE': 0.5,
        'STPIERRE': 1.1,
        'STBARTH': 1.3,
        'STMARTIN': 1.2,
        'WALLIS': 0.8,
        'POLYNESIE': 0.85,
        'CALEDONIE': 0.9
    }
    
    factor = territory_factor.get(territory_code, 1.0)
    
    # Catégories de base avec ajustements selon le territoire
    categories_base = {
        'RETRAITE_GENERALE': {
            'nom_complet': 'Retraite générale CNAV',
            'categorie': 'Régime général',
            'sous_categorie': 'Retraite de base',
            'montant_moyen': 1250 * factor,
            'nombre_beneficiaires': 120000 * factor,
            'couleur': '#28a745',
            'poids_total': 45.2 * factor,
            'evolution_annuelle': 2.3,
            'description': 'Retraite du régime général de la sécurité sociale'
        },
        'RETRAITE_COMPLEMENTAIRE': {
            'nom_complet': 'Retraite complémentaire AGIRC-ARRCO',
            'categorie': 'Régime complémentaire',
            'sous_categorie': 'Points de retraite',
            'montant_moyen': 650 * factor,
            'nombre_beneficiaires': 95000 * factor,
            'couleur': '#20c997',
            'poids_total': 25.8 * factor,
            'evolution_annuelle': 2.8,
            'description': 'Retraite complémentaire des salariés du secteur privé'
        },
        'RETRAITE_FONCTIONNAIRE': {
            'nom_complet': 'Retraite fonction publique',
            'categorie': 'Régime spécial',
            'sous_categorie': 'Fonctionnaires',
            'montant_moyen': 2200 * factor,
            'nombre_beneficiaires': 35000 * factor,
            'couleur': '#fd7e14',
            'poids_total': 18.5 * factor,
            'evolution_annuelle': 1.9,
            'description': 'Retraite des fonctionnaires de l\'État, territoriaux et hospitaliers'
        },
        'RETRAITE_AGRICOLE': {
            'nom_complet': 'Retraite agricole MSA',
            'categorie': 'Régime spécial',
            'sous_categorie': 'Agriculteurs',
            'montant_moyen': 850 * factor,
            'nombre_beneficiaires': 15000 * factor,
            'couleur': '#6f42c1',
            'poids_total': 5.3 * factor,
            'evolution_annuelle': 1.5,
            'description': 'Retraite du régime agricole'
        },
        'RETRAITE_ARTISANALE': {
            'nom_complet': 'Retraite artisans SSI',
            'categorie': 'Régime spécial',
            'sous_categorie': 'Artisans',
            'montant_moyen': 950 * factor,
            'nombre_beneficiaires': 12000 * factor,
            'couleur': '#dc3545',
            'poids_total': 4.2 * factor,
            'evolution_annuelle': 1.8,
            'description': 'Retraite des artisans et commerçants'
        },
        'RETRAITE_INVALIDITE': {
            'nom_complet': 'Pension d\'invalidité',
            'categorie': 'Pensions spécifiques',
            'sous_categorie': 'Invalidité',
            'montant_moyen': 800 * factor,
            'nombre_beneficiaires': 8000 * factor,
            'couleur': '#ffc107',
            'poids_total': 2.7 * factor,
            'evolution_annuelle': 0.8,
            'description': 'Pension d\'invalidité pour incapacité de travail'
        },
        'RETRAITE_VEUVAGE': {
            'nom_complet': 'Pension de veuvage',
            'categorie': 'Pensions spécifiques',
            'sous_categorie': 'Veuvage',
            'montant_moyen': 600 * factor,
            'nombre_beneficiaires': 18000 * factor,
            'couleur': '#6610f2',
            'poids_total': 3.8 * factor,
            'evolution_annuelle': -0.5,
            'description': 'Pension versée au conjoint survivant'
        },
        'RETRAITE_ORPHELIN': {
            'nom_complet': 'Pension d\'orphelin',
            'categorie': 'Pensions spécifiques',
            'sous_categorie': 'Orphelin',
            'montant_moyen': 300 * factor,
            'nombre_beneficiaires': 5000 * factor,
            'couleur': '#e83e8c',
            'poids_total': 0.8 * factor,
            'evolution_annuelle': -1.2,
            'description': 'Pension versée aux enfants de parents décédés'
        },
        'RETRAITE_MINIMUM_VIEILLESSE': {
            'nom_complet': 'Minimum vieillesse (ASPA)',
            'categorie': 'Solidarité',
            'sous_categorie': 'Minimum vieillesse',
            'montant_moyen': 750 * factor,
            'nombre_beneficiaires': 22000 * factor,
            'couleur': '#0066CC',
            'poids_total': 5.5 * factor,
            'evolution_annuelle': 3.2,
            'description': 'Allocation de solidarité aux personnes âgées'
        },
        'RETRAITE_COMPLEMENTAIRE_VOLONTAIRE': {
            'nom_complet': 'Retraite complémentaire volontaire',
            'categorie': 'Épargne retraite',
            'sous_categorie': 'PER, Madelin...',
            'montant_moyen': 450 * factor,
            'nombre_beneficiaires': 15000 * factor,
            'couleur': '#17a2b8',
            'poids_total': 2.2 * factor,
            'evolution_annuelle': 4.5,
            'description': 'Dispositifs d\'épargne retraite volontaire'
        }
    }
    
    # Ajustements spécifiques selon le territoire
    if territory_code == 'POLYNESIE':
        categories_base['RETRAITE_POLYNESIE'] = {
            'nom_complet': 'Régime de retraite polynésien',
            'categorie': 'Régime local',
            'sous_categorie': 'Retraite locale',
            'montant_moyen': 950 * factor,
            'nombre_beneficiaires': 25000 * factor,
            'couleur': '#0077be',
            'poids_total': 12.0 * factor,
            'evolution_annuelle': 2.5,
            'description': 'Régime de retraite spécifique à la Polynésie française'
        }
    
    elif territory_code == 'CALEDONIE':
        categories_base['RETRAITE_CALEDONIE'] = {
            'nom_complet': 'Régime de retraite calédonien',
            'categorie': 'Régime local',
            'sous_categorie': 'Retraite locale',
            'montant_moyen': 1100 * factor,
            'nombre_beneficiaires': 22000 * factor,
            'couleur': '#8B4513',
            'poids_total': 10.0 * factor,
            'evolution_annuelle': 2.2,
            'description': 'Régime de retraite spécifique à la Nouvelle-Calédonie'
        }
    
    return categories_base

@st.cache_data(ttl=1800)
def generate_historical_data(territory_code, categories):
    """Génère les données historiques optimisées"""
    dates = pd.date_range('2015-01-01', datetime.now(), freq='M')
    data = []
    
    for date in dates:
        # Impact des réformes des retraites
        if date.year == 2019:
            reforme_impact = random.uniform(1.0, 1.1)
        elif date.year == 2020:
            reforme_impact = random.uniform(0.95, 1.05)
        else:
            reforme_impact = random.uniform(1.0, 1.05)
        
        # Variation saisonnière (généralement faible pour les retraites)
        seasonal_impact = random.uniform(0.98, 1.02)
        
        for categorie_code, info in categories.items():
            base_pension = info['montant_moyen'] * info['nombre_beneficiaires']
            pension = base_pension * reforme_impact * seasonal_impact * random.uniform(0.98, 1.02)
            beneficiaires = info['nombre_beneficiaires'] * random.uniform(0.99, 1.01)
            
            data.append({
                'date': date,
                'territoire': territory_code,
                'categorie': categorie_code,
                'montant_total_pensions': pension,
                'nombre_beneficiaires': beneficiaires,
                'montant_moyen': pension / beneficiaires,
                'categorie_principale': info['categorie'],
                'evolution_mensuelle': random.uniform(-0.5, 0.5)
            })
    
    return pd.DataFrame(data)

@st.cache_data(ttl=300)
def generate_current_data(territory_code, categories, historical_data):
    """Génère les données courantes optimisées"""
    current_data = []
    
    for categorie_code, info in categories.items():
        # Dernières données historiques
        last_data = historical_data[historical_data['categorie'] == categorie_code].iloc[-1]
        
        # Variation mensuelle simulée
        change_pct = random.uniform(-0.03, 0.03)
        change_abs = last_data['montant_total_pensions'] * change_pct
        
        current_data.append({
            'territoire': territory_code,
            'categorie': categorie_code,
            'nom_complet': info['nom_complet'],
            'categorie_principale': info['categorie'],
            'montant_mensuel': last_data['montant_total_pensions'] + change_abs,
            'variation_pct': change_pct * 100,
            'variation_abs': change_abs,
            'nombre_beneficiaires': last_data['nombre_beneficiaires'] * random.uniform(0.99, 1.01),
            'montant_moyen': info['montant_moyen'] * random.uniform(0.98, 1.02),
            'poids_total': info['poids_total'],
            'montant_annee_precedente': last_data['montant_total_pensions'] * random.uniform(0.95, 1.05),
            'projection_annee_courante': last_data['montant_total_pensions'] * random.uniform(1.02, 1.04)
        })
    
    return pd.DataFrame(current_data)

@st.cache_data(ttl=600)
def generate_age_data(territory_code):
    """Génère les données par tranche d'âge optimisées"""
    age_ranges = [
        {'tranche_age': '55-59 ans', 'nombre_beneficiaires': 5000, 'montant_moyen': 800},
        {'tranche_age': '60-64 ans', 'nombre_beneficiaires': 15000, 'montant_moyen': 950},
        {'tranche_age': '65-69 ans', 'nombre_beneficiaires': 35000, 'montant_moyen': 1200},
        {'tranche_age': '70-74 ans', 'nombre_beneficiaires': 40000, 'montant_moyen': 1250},
        {'tranche_age': '75-79 ans', 'nombre_beneficiaires': 30000, 'montant_moyen': 1300},
        {'tranche_age': '80-84 ans', 'nombre_beneficiaires': 20000, 'montant_moyen': 1350},
        {'tranche_age': '85-89 ans', 'nombre_beneficiaires': 12000, 'montant_moyen': 1400},
        {'tranche_age': '90+ ans', 'nombre_beneficiaires': 8000, 'montant_moyen': 1450}
    ]
    
    # Ajustement selon le territoire
    territory_factor = {
        'REUNION': 1.0, 'GUADELOUPE': 0.95, 'MARTINIQUE': 0.9, 'GUYANE': 0.7,
        'MAYOTTE': 0.5, 'STPIERRE': 0.3, 'STBARTH': 0.4, 'STMARTIN': 0.45,
        'WALLIS': 0.25, 'POLYNESIE': 0.8, 'CALEDONIE': 0.85
    }
    
    factor = territory_factor.get(territory_code, 1.0)
    for age_range in age_ranges:
        age_range['nombre_beneficiaires'] *= factor
        age_range['montant_moyen'] *= factor
    
    return pd.DataFrame(age_ranges)

@st.cache_data(ttl=3600)
def generate_comparison_data(territories):
    """Génère les données de comparaison entre territoires"""
    comparison_data = []
    
    for territory_code, territory_info in territories.items():
        if not territory_info['retraites_actif']:
            continue
            
        categories = get_categories_retraites(territory_code)
        total_pensions = sum(
            categorie_info['montant_moyen'] * categorie_info['nombre_beneficiaires']
            for categorie_info in categories.values()
        )
        
        comparison_data.append({
            'territoire': territory_code,
            'nom_complet': territory_info['nom_complet'],
            'type': territory_info['type'],
            'population': territory_info['population'],
            'superficie': territory_info['superficie'],
            'pib': territory_info['pib'],
            'montant_total_pensions': total_pensions,
            'nombre_retraites': territory_info['nombre_retraites'],
            'montant_moyen_retraite': territory_info['montant_moyen_retraite'],
            'pension_par_habitant': total_pensions / territory_info['population'],
            'retraites_actif': territory_info['retraites_actif']
        })
    
    return pd.DataFrame(comparison_data)

class RetraitesDashboard:
    def __init__(self):
        self.territories = get_territories_definitions()
        
    def get_territory_data(self, territory_code):
        """Récupère les données d'un territoire avec cache"""
        if territory_code not in st.session_state.territories_data:
            with st.spinner(f"Chargement des données pour {self.territories[territory_code]['nom_complet']}..."):
                categories = get_categories_retraites(territory_code)
                historical_data = generate_historical_data(territory_code, categories)
                current_data = generate_current_data(territory_code, categories, historical_data)
                age_data = generate_age_data(territory_code)
                
                st.session_state.territories_data[territory_code] = {
                    'categories': categories,
                    'historical_data': historical_data,
                    'current_data': current_data,
                    'age_data': age_data,
                    'last_update': datetime.now()
                }
        
        return st.session_state.territories_data[territory_code]
    
    def update_live_data(self, territory_code):
        """Met à jour les données en temps réel"""
        if territory_code in st.session_state.territories_data:
            data = st.session_state.territories_data[territory_code]
            current_data = data['current_data'].copy()
            
            # Mise à jour légère des données
            for idx in current_data.index:
                if random.random() < 0.3:  # 30% de chance de changement
                    variation = random.uniform(-0.01, 0.01)
                    current_data.loc[idx, 'montant_mensuel'] *= (1 + variation)
                    current_data.loc[idx, 'variation_pct'] = variation * 100
                    current_data.loc[idx, 'nombre_beneficiaires'] *= random.uniform(0.99, 1.01)
            
            st.session_state.territories_data[territory_code]['current_data'] = current_data
            st.session_state.territories_data[territory_code]['last_update'] = datetime.now()
    
    def display_territory_selector(self):
        """Affiche le sélecteur de territoire optimisé"""
        st.markdown('<div class="territory-selector">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            territory_options = {v['nom_complet']: k for k, v in self.territories.items() if v['retraites_actif']}
            
            # Utilisation de session_state pour éviter le rerun
            current_name = self.territories[st.session_state.selected_territory]['nom_complet']
            selected_territory_name = st.selectbox(
                "🌍 SÉLECTIONNEZ UN TERRITOIRE:",
                options=list(territory_options.keys()),
                index=list(territory_options.keys()).index(current_name),
                key="territory_selector_main"
            )
            
            new_territory = territory_options[selected_territory_name]
            if new_territory != st.session_state.selected_territory:
                st.session_state.selected_territory = new_territory
                # Précharger les données en arrière-plan
                self.get_territory_data(new_territory)
                st.success(f"✅ Changement vers {selected_territory_name} effectué!")
        
        with col2:
            territory_info = self.territories[st.session_state.selected_territory]
            st.metric("Type", territory_info['type'])
        
        with col3:
            st.metric("Population", f"{territory_info['population']:,}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def display_header(self):
        """Affiche l'en-tête du dashboard"""
        territory_info = self.territories[st.session_state.selected_territory]
        
        st.markdown(f'<h1 class="main-header">👴 Dashboard Retraites - {territory_info["nom_complet"]}</h1>', 
                   unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="live-badge">🔴 DONNÉES DES RETRAITES EN TEMPS RÉEL</div>', 
                       unsafe_allow_html=True)
            st.markdown(f"**Surveillance et analyse des pensions de retraite par catégorie**")
        
        # Bannière drapeau du territoire
        st.markdown(f"""
        <div class="territory-flag {territory_info['drapeau']}">
            <strong>{territory_info['nom_complet']} - Système de Retraites</strong><br>
            <small>Type: {territory_info['type']} | Population: {territory_info['population']:,} | PIB: {territory_info['pib']} M€</small>
        </div>
        """, unsafe_allow_html=True)
        
        current_time = datetime.now().strftime('%H:%M:%S')
        st.sidebar.markdown(f"**🕐 Dernière mise à jour: {current_time}**")
    
    def display_key_metrics(self):
        """Affiche les métriques clés des retraites"""
        data = self.get_territory_data(st.session_state.selected_territory)
        current_data = data['current_data']
        
        st.markdown('<h3 class="section-header">📊 INDICATEURS CLÉS DES RETRAITES</h3>', 
                   unsafe_allow_html=True)
        
        # Calcul des métriques
        montant_total = current_data['montant_mensuel'].sum()
        variation_moyenne = current_data['variation_pct'].mean()
        beneficiaires_total = current_data['nombre_beneficiaires'].sum()
        categories_hausse = len(current_data[current_data['variation_pct'] > 0])
        
        montant_annuel_projete = montant_total * 12
        territory_info = self.territories[st.session_state.selected_territory]
        pension_par_habitant = montant_total / territory_info['population']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Montant Mensuel Total",
                f"{montant_total/1e6:.1f} M€",
                f"{variation_moyenne:+.2f}%",
                delta_color="normal"
            )
        
        with col2:
            st.metric(
                "Montant Annuel Projeté",
                f"{montant_annuel_projete/1e6:.1f} M€",
                f"{random.uniform(1, 4):.1f}% vs année précédente"
            )
        
        with col3:
            st.metric(
                "Nombre de Bénéficiaires",
                f"{beneficiaires_total:,.0f}",
                f"{random.randint(-2, 5)}% vs mois dernier"
            )
        
        with col4:
            st.metric(
                "Pension Moyenne",
                f"{montant_total/beneficiaires_total:.0f} €",
                f"{random.uniform(-1, 3):.1f}% vs période précédente"
            )
        
        # Métriques spécifiques au territoire
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Pension par Habitant",
                f"{pension_par_habitant:.0f} €",
                f"{random.uniform(-5, 5):.1f}% vs moyenne DROM-COM"
            )
        
        with col2:
            st.metric(
                "Taux de Couverture",
                f"{(beneficiaires_total/territory_info['population'])*100:.1f}%",
                f"{random.uniform(-1, 2):.1f}% vs objectif"
            )
        
        with col3:
            st.metric(
                "Contribution au PIB",
                f"{(montant_annuel_projete/territory_info['pib']/1e6)*100:.2f}%",
                f"{random.uniform(-1, 3):.1f}% vs objectif"
            )
    
    def create_retraites_overview(self):
        """Crée la vue d'ensemble des retraites"""
        data = self.get_territory_data(st.session_state.selected_territory)
        
        st.markdown('<h3 class="section-header">🏛️ VUE D\'ENSEMBLE DES RETRAITES</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["Évolution Montants", "Répartition Catégories", "Top Catégories", "Analyse Âge"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                # Évolution des montants totaux
                evolution_totale = data['historical_data'].groupby('date')['montant_total_pensions'].sum().reset_index()
                evolution_totale['montant_mensuel_M'] = evolution_totale['montant_total_pensions'] / 1e6
                
                fig = px.line(evolution_totale, 
                             x='date', 
                             y='montant_mensuel_M',
                             title=f'Évolution des Montants - {self.territories[st.session_state.selected_territory]["nom_complet"]}',
                             color_discrete_sequence=['#0055A4'])
                fig.update_layout(yaxis_title="Montants (Millions €)")
                st.plotly_chart(fig, config={'displayModeBar': False})
            
            with col2:
                # Performance par catégorie
                performance_categories = data['current_data'].groupby('categorie_principale').agg({
                    'variation_pct': 'mean',
                    'montant_mensuel': 'sum'
                }).reset_index()
                
                fig = px.bar(performance_categories, 
                            x='categorie_principale', 
                            y='variation_pct',
                            title='Performance Mensuelle par Catégorie (%)',
                            color='categorie_principale',
                            color_discrete_sequence=px.colors.qualitative.Set3)
                fig.update_layout(yaxis_title="Variation (%)")
                st.plotly_chart(fig, config={'displayModeBar': False})
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.pie(data['current_data'], 
                            values='montant_mensuel', 
                            names='categorie',
                            title='Répartition des Montants par Catégorie',
                            color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig, config={'displayModeBar': False})
            
            with col2:
                fig = px.bar(data['current_data'], 
                            x='categorie', 
                            y='nombre_beneficiaires',
                            title='Nombre de Bénéficiaires par Catégorie',
                            color_discrete_sequence=px.colors.qualitative.Set3)
                fig.update_layout(yaxis_title="Nombre de Bénéficiaires")
                st.plotly_chart(fig, config={'displayModeBar': False})
        
        with tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                top_categories = data['current_data'].nlargest(10, 'montant_mensuel')
                fig = px.bar(top_categories, 
                            x='montant_mensuel', 
                            y='categorie',
                            orientation='h',
                            title='Top 10 des Catégories par Montant Total',
                            color='montant_mensuel',
                            color_continuous_scale='Blues')
                st.plotly_chart(fig, config={'displayModeBar': False})
            
            with col2:
                top_croissance = data['current_data'].nlargest(10, 'variation_pct')
                fig = px.bar(top_croissance, 
                            x='variation_pct', 
                            y='categorie',
                            orientation='h',
                            title='Top 10 des Croissances par Catégorie (%)',
                            color='variation_pct',
                            color_continuous_scale='Greens')
                st.plotly_chart(fig, config={'displayModeBar': False})
        
        with tab4:
            st.subheader("Analyse par Tranche d'Âge")
            
            fig = px.bar(data['age_data'], 
                       x='tranche_age', 
                       y='nombre_beneficiaires',
                       title='Nombre de Bénéficiaires par Tranche d\'Âge',
                       color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig, config={'displayModeBar': False})
            
            fig = px.line(data['age_data'], 
                        x='tranche_age', 
                        y='montant_moyen',
                        title='Montant Moyen par Tranche d\'Âge',
                        color_discrete_sequence=['#0055A4'])
            st.plotly_chart(fig, config={'displayModeBar': False})
            
            st.dataframe(data['age_data'], use_container_width=True)
    
    def create_categories_live(self):
        """Affiche les catégories en temps réel"""
        data = self.get_territory_data(st.session_state.selected_territory)
        
        st.markdown('<h3 class="section-header">🏢 CATÉGORIES DE RETRAITES EN TEMPS RÉEL</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Tableau des Pensions", "Analyse Catégorie", "Simulateur"])
        
        with tab1:
            col1, col2, col3 = st.columns(3)
            with col1:
                categorie_filtre = st.selectbox("Catégorie:", 
                                              ['Toutes'] + list(data['current_data']['categorie_principale'].unique()))
            with col2:
                performance_filtre = st.selectbox("Performance:", 
                                                ['Toutes', 'En croissance', 'En décroissance', 'Stable'])
            with col3:
                tri_filtre = st.selectbox("Trier par:", 
                                        ['Montant mensuel', 'Variation %', 'Nombre bénéficiaires', 'Montant moyen'])
            
            # Application des filtres
            categories_filtrees = data['current_data'].copy()
            if categorie_filtre != 'Toutes':
                categories_filtrees = categories_filtrees[categories_filtrees['categorie_principale'] == categorie_filtre]
            if performance_filtre == 'En croissance':
                categories_filtrees = categories_filtrees[categories_filtrees['variation_pct'] > 0]
            elif performance_filtre == 'En décroissance':
                categories_filtrees = categories_filtrees[categories_filtrees['variation_pct'] < 0]
            elif performance_filtre == 'Stable':
                categories_filtrees = categories_filtrees[categories_filtrees['variation_pct'] == 0]
            
            # Tri
            if tri_filtre == 'Montant mensuel':
                categories_filtrees = categories_filtrees.sort_values('montant_mensuel', ascending=False)
            elif tri_filtre == 'Variation %':
                categories_filtrees = categories_filtrees.sort_values('variation_pct', ascending=False)
            elif tri_filtre == 'Nombre bénéficiaires':
                categories_filtrees = categories_filtrees.sort_values('nombre_beneficiaires', ascending=False)
            elif tri_filtre == 'Montant moyen':
                categories_filtrees = categories_filtrees.sort_values('montant_moyen', ascending=False)
            
            # Affichage optimisé
            for _, categorie in categories_filtrees.iterrows():
                change_class = "positive" if categorie['variation_pct'] > 0 else "negative" if categorie['variation_pct'] < 0 else "neutral"
                
                col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 1, 1])
                with col1:
                    st.markdown(f"**{categorie['categorie']}**")
                    st.markdown(f"*{categorie['categorie_principale']}*")
                with col2:
                    st.markdown(f"**{categorie['nom_complet']}**")
                    st.markdown(f"Montant moyen: {categorie['montant_moyen']:.0f}€")
                with col3:
                    st.markdown(f"**{categorie['montant_mensuel']/1e6:.1f}M€**")
                    st.markdown(f"Bénéficiaires: {categorie['nombre_beneficiaires']:,.0f}")
                with col4:
                    variation_str = f"{categorie['variation_pct']:+.2f}%"
                    st.markdown(f"**{variation_str}**")
                    st.markdown(f"{categorie['variation_abs']/1e3:+.0f}K€")
                with col5:
                    st.markdown(f"<div class='pension-change {change_class}'>{variation_str}</div>", 
                               unsafe_allow_html=True)
                    st.markdown(f"Poids: {categorie['poids_total']:.1f}%")
                
                st.markdown("---")
        
        with tab2:
            categorie_selectionnee = st.selectbox("Sélectionnez une catégorie:", 
                                                data['current_data']['categorie_principale'].unique())
            
            if categorie_selectionnee:
                categories_categorie = data['current_data'][
                    data['current_data']['categorie_principale'] == categorie_selectionnee
                ]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.bar(categories_categorie, 
                                x='categorie', 
                                y='variation_pct',
                                title=f'Performance des Catégories - {categorie_selectionnee}',
                                color='variation_pct',
                                color_continuous_scale='RdYlGn')
                    st.plotly_chart(fig, config={'displayModeBar': False})
                
                with col2:
                    fig = px.pie(categories_categorie, 
                                values='montant_mensuel', 
                                names='categorie',
                                title=f'Répartition des Montants - {categorie_selectionnee}')
                    st.plotly_chart(fig, config={'displayModeBar': False})
        
        with tab3:
            st.subheader("Simulateur de Calcul de Retraite")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                categorie_selectionnee = st.selectbox("Catégorie de retraite:", 
                                                     data['current_data']['categorie'].unique())
                age_depart = st.number_input("Âge de départ:", 
                                           min_value=55, max_value=70, value=62)
            with col2:
                salaire_moyen = st.number_input("Salaire moyen des 25 meilleures années (€):", 
                                              min_value=1000.0, value=2500.0)
                trimestres_valides = st.number_input("Nombre de trimestres validés:", 
                                                   min_value=0, max_value=200, value=160)
            with col3:
                type_taux = st.selectbox("Type de calcul:", 
                                       ["Taux plein", "Taux réduit", "Décote"])
                calculer = st.button("Calculer la Retraite")
            
            if calculer:
                categorie_data = data['current_data'][
                    data['current_data']['categorie'] == categorie_selectionnee
                ].iloc[0]
                
                # Calcul simplifié de la pension
                if type_taux == "Taux plein":
                    taux = 0.5
                elif type_taux == "Taux réduit":
                    taux = 0.4
                else:  # Décote
                    taux = max(0.375, 0.5 - (0.625 * max(0, 162 - trimestres_valides) / 162))
                
                pension_estimee = salaire_moyen * taux
                
                st.success(f"""
                **Résultat du calcul:**
                - Catégorie: {categorie_data['nom_complet']}
                - Âge de départ: {age_depart} ans
                - Taux appliqué: {taux*100:.1f}%
                - Salaire de référence: {salaire_moyen:,.2f}€
                - **Pension mensuelle estimée: {pension_estimee:,.2f}€**
                - Pension annuelle estimée: {pension_estimee*12:,.2f}€
                """)
    
    def create_categorie_analysis(self):
        """Analyse par catégorie détaillée"""
        data = self.get_territory_data(st.session_state.selected_territory)
        
        st.markdown('<h3 class="section-header">📊 ANALYSE PAR CATÉGORIE DÉTAILLÉE</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Performance Catégorielle", "Comparaison Catégories", "Tendances"])
        
        with tab1:
            categorie_performance = data['current_data'].groupby('categorie_principale').agg({
                'variation_pct': 'mean',
                'nombre_beneficiaires': 'sum',
                'montant_mensuel': 'sum',
                'categorie': 'count'
            }).reset_index()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(categorie_performance, 
                            x='categorie_principale', 
                            y='variation_pct',
                            title='Performance Moyenne par Catégorie (%)',
                            color='variation_pct',
                            color_continuous_scale='RdYlGn')
                st.plotly_chart(fig, config={'displayModeBar': False})
            
            with col2:
                fig = px.scatter(categorie_performance, 
                               x='montant_mensuel', 
                               y='variation_pct',
                               size='nombre_beneficiaires',
                               color='categorie_principale',
                               title='Performance vs Montants par Catégorie',
                               hover_name='categorie_principale',
                               size_max=60)
                st.plotly_chart(fig, config={'displayModeBar': False})
        
        with tab2:
            categorie_evolution = data['historical_data'].groupby([
                data['historical_data']['date'].dt.to_period('M').dt.to_timestamp(),
                'categorie_principale'
            ])['montant_total_pensions'].sum().reset_index()
            
            fig = px.line(categorie_evolution, 
                         x='date', 
                         y='montant_total_pensions',
                         color='categorie_principale',
                         title=f'Évolution Comparative - {self.territories[st.session_state.selected_territory]["nom_complet"]}',
                         color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(yaxis_title="Montants des Pensions (€)")
            st.plotly_chart(fig, config={'displayModeBar': False})
        
        with tab3:
            st.subheader("Tendances et Perspectives par Catégorie")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ### 📈 Catégories en Croissance
                
                **🏥 Retraite complémentaire:**
                - Augmentation du nombre de cotisants
                - Amélioration des taux de remplacement
                - Réformes favorisant l'épargne retraite
                
                **👴 Minimum vieillesse (ASPA):**
                - Vieillissement de la population
                - Amélioration de l'accès aux droits
                - Revalorisation régulière des montants
                
                **💰 Retraite complémentaire volontaire:**
                - Prise de conscience de la nécessité d'épargner
                - Avantages fiscaux renforcés
                - Développement de nouveaux produits d'épargne
                """)
            
            with col2:
                st.markdown("""
                ### 📉 Catégories en Décroissance
                
                **👨‍🌾 Retraite agricole:**
                - Diminution du nombre d'agriculteurs
                - Modernisation du secteur
                - Regroupement des exploitations
                
                **👶 Pension d'orphelin:**
                - Baisse de la mortalité parentale
                - Amélioration des conditions de vie
                - Politiques familiales
                
                **💔 Pension de veuvage:**
                - Augmentation de l'espérance de vie masculine
                - Évolution des structures familiales
                - Autonomisation financière des femmes
                """)
    
    def create_evolution_analysis(self):
        """Analyse de l'évolution des pensions"""
        data = self.get_territory_data(st.session_state.selected_territory)
        
        st.markdown('<h3 class="section-header">📈 ÉVOLUTION DES PENSIONS</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Analyse Historique", "Projections Démographiques", "Réformes Impact"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                cumulative_data = data['historical_data'].copy()
                cumulative_data['date_group'] = cumulative_data['date'].dt.to_period('M').dt.to_timestamp()
                monthly_totals = cumulative_data.groupby('date_group')['montant_total_pensions'].sum().reset_index()
                monthly_totals['cumulative_pensions'] = monthly_totals['montant_total_pensions'].cumsum()
                
                fig = px.line(monthly_totals, 
                             x='date_group', 
                             y='cumulative_pensions',
                             title=f'Montants Cumulatifs - {self.territories[st.session_state.selected_territory]["nom_complet"]} (€)')
                st.plotly_chart(fig, config={'displayModeBar': False})
            
            with col2:
                monthly_heatmap = monthly_totals.copy()
                monthly_heatmap['annee'] = monthly_heatmap['date_group'].dt.year
                monthly_heatmap['mois'] = monthly_heatmap['date_group'].dt.month
                
                heatmap_data = monthly_heatmap.pivot(index='annee', columns='mois', values='montant_total_pensions')
                
                fig = px.imshow(heatmap_data, 
                               labels=dict(x="Mois", y="Année", color="Montant (€)"),
                               x=["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"],
                               title='Heatmap Mensuel des Montants de Pensions')
                st.plotly_chart(fig, config={'displayModeBar': False})
        
        with tab2:
            st.subheader("Projections Démographiques et Impact sur les Retraites")
            
            # Données de projection simulées
            years = list(range(2023, 2043))
            projection_data = []
            
            for year in years:
                # Simulation de l'évolution démographique
                age_65_plus = data['age_data'][data['age_data']['tranche_age'].str.contains('65+')]['nombre_beneficiaires'].sum()
                population_65_plus = age_65_plus * (1 + (year - 2023) * 0.02)  # Croissance de 2% par an
                
                # Simulation de l'évolution des pensions
                total_pensions = data['current_data']['montant_mensuel'].sum() * 12
                projected_pensions = total_pensions * (1 + (year - 2023) * 0.025)  # Croissance de 2.5% par an
                
                projection_data.append({
                    'année': year,
                    'population_65_plus': population_65_plus,
                    'montant_total_pensions': projected_pensions,
                    'pension_moyenne': projected_pensions / population_65_plus
                })
            
            projection_df = pd.DataFrame(projection_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.line(projection_df, 
                             x='année', 
                             y='population_65_plus',
                             title='Projection de la Population de 65+',
                             color_discrete_sequence=['#0055A4'])
                fig.update_layout(yaxis_title="Population")
                st.plotly_chart(fig, config={'displayModeBar': False})
            
            with col2:
                fig = px.line(projection_df, 
                             x='année', 
                             y='montant_total_pensions',
                             title='Projection du Montant Total des Pensions',
                             color_discrete_sequence=['#EF4135'])
                fig.update_layout(yaxis_title="Montant Total (€)")
                st.plotly_chart(fig, config={'displayModeBar': False})
            
            st.dataframe(projection_df, use_container_width=True)
        
        with tab3:
            st.subheader("Impact des Réformes des Retraites")
            
            # Données simulées d'impact des réformes
            reformes_data = [
                {'reforme': 'Réforme 2014 (Touraine)', 'année': 2014, 'impact_pct': 0.8, 'description': 'Allongement de la durée de cotisation'},
                {'reforme': 'Réforme 2020 (Delevoye)', 'année': 2020, 'impact_pct': 1.2, 'description': 'Système universel par points'},
                {'reforme': 'Réforme 2023', 'année': 2023, 'impact_pct': 2.5, 'description': 'Report de l\'âge légal de départ'},
                {'reforme': 'Prochaine réforme', 'année': 2027, 'impact_pct': 1.8, 'description': 'Projet en discussion'}
            ]
            
            reformes_df = pd.DataFrame(reformes_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(reformes_df, 
                            x='reforme', 
                            y='impact_pct',
                            title='Impact des Réformes sur les Pensions (%)',
                            color='impact_pct',
                            color_continuous_scale='RdYlGn')
                st.plotly_chart(fig, config={'displayModeBar': False})
            
            with col2:
                fig = px.scatter(reformes_df, 
                               x='année', 
                               y='impact_pct',
                               size='impact_pct',
                               color='reforme',
                               title='Chronologie des Réformes et Impact',
                               hover_name='reforme',
                               size_max=60)
                st.plotly_chart(fig, config={'displayModeBar': False})
            
            for _, reforme in reformes_df.iterrows():
                st.markdown(f"""
                **{reforme['reforme']} ({reforme['année']})**: {reforme['description']}
                - Impact estimé: {reforme['impact_pct']}%
                """)
    
    def create_comparison_territories(self):
        """Crée une vue de comparaison entre territoires"""
        st.markdown('<h3 class="section-header">🌍 COMPARAISON INTER-TERRITOIRES</h3>', 
                   unsafe_allow_html=True)
        
        comparison_data = generate_comparison_data(self.territories)
        
        tab1, tab2, tab3 = st.tabs(["Comparaison Globale", "Indicateurs par Territoire", "Classement"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(comparison_data, 
                            x='nom_complet', 
                            y='montant_total_pensions',
                            title='Montant Total des Pensions par Territoire',
                            color='type',
                            color_discrete_sequence=px.colors.qualitative.Set3)
                fig.update_layout(yaxis_title="Montant Total (€)")
                st.plotly_chart(fig, config={'displayModeBar': False})
            
            with col2:
                fig = px.bar(comparison_data, 
                            x='nom_complet', 
                            y='nombre_retraites',
                            title='Nombre de Retraités par Territoire',
                            color='type',
                            color_discrete_sequence=px.colors.qualitative.Set3)
                fig.update_layout(yaxis_title="Nombre de Retraités")
                st.plotly_chart(fig, config={'displayModeBar': False})
        
        with tab2:
            selected_territories = st.multiselect(
                "Sélectionnez les territoires à comparer:",
                options=comparison_data['nom_complet'].tolist(),
                default=comparison_data['nom_complet'].tolist()[:5]
            )
            
            if selected_territories:
                filtered_data = comparison_data[comparison_data['nom_complet'].isin(selected_territories)]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.scatter(filtered_data, 
                                   x='pib', 
                                   y='montant_total_pensions',
                                   size='population',
                                   color='nom_complet',
                                   title='PIB vs Montant Total des Pensions',
                                   hover_name='nom_complet',
                                   size_max=60)
                    st.plotly_chart(fig, config={'displayModeBar': False})
                
                with col2:
                    fig = px.scatter(filtered_data, 
                                   x='montant_moyen_retraite', 
                                   y='pension_par_habitant',
                                   size='population',
                                   color='nom_complet',
                                   title='Pension Moyenne vs Pension par Habitant',
                                   hover_name='nom_complet',
                                   size_max=60)
                    st.plotly_chart(fig, config={'displayModeBar': False})
                
                st.dataframe(filtered_data, use_container_width=True)
        
        with tab3:
            st.subheader("Classement des Territoires")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Par Montant Total des Pensions:**")
                top_pensions = comparison_data.sort_values('montant_total_pensions', ascending=False)
                for i, (_, row) in enumerate(top_pensions.iterrows()):
                    st.markdown(f"{i+1}. {row['nom_complet']}: {row['montant_total_pensions']/1e6:.1f} M€")
            
            with col2:
                st.markdown("**Par Pension Moyenne:**")
                top_moyenne = comparison_data.sort_values('montant_moyen_retraite', ascending=False)
                for i, (_, row) in enumerate(top_moyenne.iterrows()):
                    st.markdown(f"{i+1}. {row['nom_complet']}: {row['montant_moyen_retraite']:.0f} €")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Par Nombre de Retraités:**")
                top_nombre = comparison_data.sort_values('nombre_retraites', ascending=False)
                for i, (_, row) in enumerate(top_nombre.iterrows()):
                    st.markdown(f"{i+1}. {row['nom_complet']}: {row['nombre_retraites']:,}")
            
            with col2:
                st.markdown("**Par Pension par Habitant:**")
                top_par_habitant = comparison_data.sort_values('pension_par_habitant', ascending=False)
                for i, (_, row) in enumerate(top_par_habitant.iterrows()):
                    st.markdown(f"{i+1}. {row['nom_complet']}: {row['pension_par_habitant']:.0f} €")
    
    def run(self):
        """Fonction principale pour exécuter le dashboard"""
        self.display_territory_selector()
        self.display_header()
        self.display_key_metrics()
        
        # Mise à jour automatique des données
        if st.sidebar.button("🔄 Mettre à jour les données"):
            self.update_live_data(st.session_state.selected_territory)
            st.success("✅ Données mises à jour avec succès!")
        
        # Création des onglets
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Vue d'ensemble", 
            "Catégories en direct", 
            "Analyse par catégorie", 
            "Évolution et projections",
            "Comparaison territoires"
        ])
        
        with tab1:
            self.create_retraites_overview()
        
        with tab2:
            self.create_categories_live()
        
        with tab3:
            self.create_categorie_analysis()
        
        with tab4:
            self.create_evolution_analysis()
        
        with tab5:
            self.create_comparison_territories()
        
        # Footer
        st.markdown("---")
        st.markdown("**Dashboard des Retraites DROM-COM** | Données mises à jour en temps réel | Source: Services des Retraites")

# Exécution du dashboard
if __name__ == "__main__":
    dashboard = RetraitesDashboard()
    dashboard.run()