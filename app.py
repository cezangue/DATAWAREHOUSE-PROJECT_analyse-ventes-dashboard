import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import base64
import os
from pathlib import Path

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Système d'Analyse des Ventes",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Fonction pour ajouter les styles CSS
def add_bg_and_styling():
    st.markdown("""
    <style>
        /* Style global */
        .stApp {
            background-color: #f0f2f6;
        }
        
        /* Header styling */
        .main-header {
            background-color: #0e4c92;
            color: white;
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Navigation button styling */
        .nav-button {
            background-color: #0281b8;
            color: white;
            padding: 15px 20px;
            text-align: center;
            text-decoration: none;
            display: block;
            border-radius: 8px;
            margin: 10px 0px;
            font-size: 1.2rem;
            font-weight: 500;
            transition: all 0.3s;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
            border: none;
            cursor: pointer;
            width: 100%;
        }
        
        .nav-button:hover {
            background-color: #026da3;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            transform: translateY(-2px);
        }
        
        /* Footer styling */
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #0e4c92;
            color: white;
            text-align: center;
            padding: 10px 0;
            font-size: 0.9rem;
        }
        
        /* Card styling */
        .card {
            background-color: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: #f0f2f6;
            border-radius: 4px 4px 0px 0px;
            padding: 10px 20px;
            font-weight: 500;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #0281b8;
            color: white;
        }
        
        /* Metric styling */
        [data-testid="stMetricValue"] {
            font-size: 1.5rem;
            font-weight: bold;
            color: #0e4c92;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Enhance tables */
        .dataframe {
            border-collapse: collapse;
            width: 100%;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        
        .dataframe th {
            background-color: #0e4c92;
            color: white;
            padding: 12px 15px;
            text-align: left;
        }
        
        .dataframe td {
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .dataframe tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        
        .dataframe tr:hover {
            background-color: #f1f1f1;
        }
        
        /* Modify plotly charts styling */
        .js-plotly-plot .plotly .modebar {
            right: 10px !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Fonction pour charger les données
@st.cache_data
def load_data(uploaded_file=None):
    try:
        if uploaded_file is None:
            if 'data' in st.session_state and st.session_state.data is not None:
                return st.session_state.data
            st.error("Aucun fichier de données n'a été uploadé.")
            st.info("Veuillez télécharger votre fichier dans la section 'Browse Files'.")
            return pd.DataFrame()
        
        # Charger le fichier uploadé
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Vérification des colonnes nécessaires
        required_columns = ['Country', 'Month', 'CustomerID', 'ProductName', 'QuantiteVendue', 'MontantVentes']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Les colonnes suivantes sont manquantes dans votre fichier : {', '.join(missing_columns)}")
            st.error("Veuillez uploader un fichier avec les colonnes requises.")
            return pd.DataFrame()
        
        # Création de MonthOrder si absent
        if 'MonthOrder' not in df.columns:
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            month_order = {month: i for i, month in enumerate(months)}
            if set(df['Month'].unique()).issubset(set(months)):
                df['MonthOrder'] = df['Month'].map(month_order)
            else:
                st.warning("Format des mois non reconnu. Ordre chronologique peut être incorrect.")
                unique_months = df['Month'].unique()
                custom_order = {month: i for i, month in enumerate(unique_months)}
                df['MonthOrder'] = df['Month'].map(custom_order)
        
        st.success(f"Données chargées avec succès depuis {uploaded_file.name}")
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        return pd.DataFrame()

# Fonction pour sauvegarder un fichier uploadé
def save_uploaded_file(uploaded_file):
    try:
        with open("merged_data.csv", "wb") as f:
            f.write(uploaded_file.getbuffer())
        return True
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde du fichier : {e}")
        return False

# Appliquer les styles
add_bg_and_styling()

# Définir les pages
def page_home():
    st.markdown('<div class="main-header"><h1>Système d\'Analyse des Ventes</h1></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        for label, page, help_text in [
            ('Browse Files', 'browse_files', 'Parcourir les fichiers de données'),
            ('Create New', 'create_new', 'Créer une nouvelle analyse'),
            ('Manage Data Sources', 'manage_data', 'Gérer les sources de données'),
            ('Documentation', 'documentation', 'Consulter la documentation')
        ]:
            if st.button(label, key=f'btn_{page}', help=help_text, use_container_width=True):
                st.session_state.page = page
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        for label, page, help_text in [
            ('Analysis Report', 'analysis_report', 'Voir le rapport d\'analyse'),
            ('Interactive Report', 'interactive_report', 'Consulter le rapport interactif'),
            ('Dashboard', 'dashboard', 'Afficher le tableau de bord')
        ]:
            if st.button(label, key=f'btn_{page}', help=help_text, use_container_width=True):
                st.session_state.page = page
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("""
    ## À propos du Système d'Analyse des Ventes
    
    Ce système vous permet d'analyser les données de ventes de votre entreprise de manière intuitive et interactive.
    Utilisez les boutons ci-dessus pour naviguer entre les différentes fonctionnalités.
    
    ### Principales fonctionnalités:
    
    * **Analysis Report**: Rapports détaillés sur les ventes par pays et par mois
    * **Interactive Report**: Rapport interactif permettant de filtrer et d'explorer les données
    * **Dashboard**: Tableau de bord visuel avec graphiques interactifs
    """)
    
    if 'data' in st.session_state and st.session_state.data is not None:
        st.success("Données chargées. Vous pouvez accéder aux analyses.")
    else:
        st.warning("Aucune donnée chargée. Veuillez uploader un fichier dans 'Browse Files'.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("""
    ## Comment utiliser le système
    
    Suivez ces étapes simples pour commencer :
    
    1. **Importez vos données** : Rendez-vous dans "Browse Files" pour uploader un fichier CSV ou Excel contenant vos données de ventes.
    2. **Vérifiez les données** : Assurez-vous que votre fichier inclut les colonnes requises (Country, Month, CustomerID, ProductName, QuantiteVendue, MontantVentes).
    3. **Explorez les analyses** : Utilisez les boutons "Analysis Report", "Interactive Report" ou "Dashboard" pour visualiser et analyser vos données.
    4. **Consultez la documentation** : Pour plus d'informations, visitez la page "Documentation".
    
    Commencez dès maintenant en cliquant sur "Browse Files" pour importer vos données !
    """)
    st.markdown('</div>', unsafe_allow_html=True)

def page_browse_files():
    st.markdown('<div class="main-header"><h1>Browse Files</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Téléchargez votre fichier de données", type=["csv", "xlsx", "xls"])
    
    if uploaded_file is not None:
        st.write(f"Nom du fichier : {uploaded_file.name}")
        st.write(f"Type du fichier : {uploaded_file.type}")
        st.write(f"Taille du fichier : {uploaded_file.size} bytes")
        
        df = load_data(uploaded_file)
        if not df.empty:
            st.session_state.data = df
            st.write("Aperçu des données :")
            st.dataframe(df.head())
            st.write("Statistiques des données :")
            st.write(df.describe())
            st.write("Colonnes disponibles :")
            st.write(", ".join(df.columns.tolist()))
            
            if st.button("Utiliser ce fichier comme source de données"):
                if save_uploaded_file(uploaded_file):
                    st.success(f"Fichier {uploaded_file.name} sauvegardé comme source de données.")
                    st.rerun()
    
    st.markdown("Cette section vous permet de parcourir et de télécharger vos fichiers de données pour analyse.")
    if st.button("Retour à l'accueil"):
        st.session_state.page = 'home'
    st.markdown('</div>', unsafe_allow_html=True)

def page_create_new():
    st.markdown('<div class="main-header"><h1>Create New Analysis</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("Cette section vous permet de créer de nouvelles analyses à partir de vos données.")
    if st.button("Retour à l'accueil"):
        st.session_state.page = 'home'
    st.markdown('</div>', unsafe_allow_html=True)

def page_manage_data():
    st.markdown('<div class="main-header"><h1>Manage Data Sources</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    st.subheader("Fichiers de données disponibles")
    files = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx', '.xls'))]
    if files:
        for file in files:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"📄 {file}")
            with col2:
                if st.button(f"Aperçu", key=f"preview_{file}"):
                    try:
                        df = pd.read_csv(file) if file.endswith('.csv') else pd.read_excel(file)
                        st.session_state.preview_file = file
                        st.session_state.preview_df = df
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur lors de la lecture du fichier : {e}")
            with col3:
                if st.button(f"Utiliser", key=f"use_{file}"):
                    try:
                        df = pd.read_csv(file) if file.endswith('.csv') else pd.read_excel(file)
                        st.session_state.data = df
                        df.to_csv("merged_data.csv", index=False)
                        st.success(f"Le fichier {file} est maintenant utilisé comme source de données principale.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur lors de la définition du fichier comme source principale : {e}")
    else:
        st.info("Aucun fichier de données disponible. Veuillez télécharger un fichier dans la section 'Browse Files'.")
    
    if 'preview_file' in st.session_state and 'preview_df' in st.session_state:
        st.subheader(f"Aperçu de {st.session_state.preview_file}")
        st.dataframe(st.session_state.preview_df.head())
        st.write(f"Nombre total de lignes : {len(st.session_state.preview_df)}")
        st.write(f"Colonnes disponibles : {', '.join(st.session_state.preview_df.columns.tolist())}")
        if st.button("Fermer l'aperçu"):
            del st.session_state.preview_file
            del st.session_state.preview_df
            st.rerun()
    
    st.markdown("Cette section vous permet de gérer vos sources de données pour les analyses.")
    if st.button("Retour à l'accueil"):
        st.session_state.page = 'home'
    st.markdown('</div>', unsafe_allow_html=True)

def page_documentation():
    st.markdown('<div class="main-header"><h1>Documentation</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("""
    ## Documentation du Système d'Analyse des Ventes
    
    ### Introduction
    Ce système vous permet d'analyser les données de ventes de votre entreprise par pays, par mois, par client et par produit.
    
    ### Comment utiliser le système
    1. **Browse Files**: Importez vos fichiers CSV ou Excel contenant vos données de ventes
    2. **Create New**: Créez de nouvelles analyses personnalisées
    3. **Analysis Report**: Consultez des rapports prédéfinis sur vos ventes
    4. **Interactive Report**: Explorez vos données de manière interactive
    5. **Dashboard**: Visualisez vos données à l'aide de graphiques interactifs
    
    ### Structure des données
    Les données doivent contenir les colonnes suivantes:
    - Country: Pays où la vente a été réalisée
    - Month: Mois de la vente
    - CustomerID: Identifiant du client
    - ProductName: Nom du produit
    - QuantiteVendue: Quantité vendue
    - MontantVentes: Montant total des ventes
    """)
    if st.button("Retour à l'accueil"):
        st.session_state.page = 'home'
    st.markdown('</div>', unsafe_allow_html=True)

def page_analysis_report():
    st.markdown('<div class="main-header"><h1>Analysis Report</h1></div>', unsafe_allow_html=True)
    
    if 'data' not in st.session_state or st.session_state.data is None:
        st.error("Aucune donnée disponible. Veuillez importer un fichier de données valide dans 'Browse Files'.")
        if st.button("Retour à l'accueil"):
            st.session_state.page = 'home'
        return
    
    df = st.session_state.data
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("## Rapport d'analyse des ventes")
    
    total_sales = df['MontantVentes'].sum()
    avg_sales = df['MontantVentes'].mean()
    total_quantity = df['QuantiteVendue'].sum()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Ventes Totales", f"{total_sales:,.2f} €")
    col2.metric("Vente Moyenne", f"{avg_sales:.2f} €")
    col3.metric("Quantité Totale", f"{total_quantity}")
    
    st.write("### Top des pays par ventes")
    top_countries = df.groupby('Country')['MontantVentes'].sum().sort_values(ascending=False).reset_index()
    st.dataframe(top_countries, use_container_width=True)
    
    st.write("### Évolution mensuelle des ventes")
    monthly_sales = df.groupby(['Month', 'MonthOrder'])['MontantVentes'].sum().reset_index().sort_values('MonthOrder')
    
    fig = px.line(monthly_sales, x='Month', y='MontantVentes',
                 labels={'MontantVentes': 'Ventes Totales', 'Month': 'Mois'},
                 markers=True)
    fig.update_layout(xaxis_title="Mois", yaxis_title="Ventes Totales", height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    if st.button("Retour à l'accueil"):
        st.session_state.page = 'home'
    st.markdown('</div>', unsafe_allow_html=True)

def page_interactive_report():
    st.markdown('<div class="main-header"><h1>Interactive Report</h1></div>', unsafe_allow_html=True)
    
    if 'data' not in st.session_state or st.session_state.data is None:
        st.error("Aucune donnée disponible. Veuillez importer un fichier de données valide dans 'Browse Files'.")
        if st.button("Retour à l'accueil"):
            st.session_state.page = 'home'
        return
    
    df = st.session_state.data
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("## Filtres")
    
    col1, col2 = st.columns(2)
    with col1:
        countries = sorted(df['Country'].unique())
        selected_countries = st.multiselect("Sélectionner des pays", options=countries, default=countries)
    
    with col2:
        months = sorted(df['Month'].unique(), key=lambda x: df[df['Month']==x]['MonthOrder'].iloc[0])
        selected_months = st.multiselect("Sélectionner des mois", options=months, default=months)
    
    if not selected_countries or not selected_months:
        st.warning("Veuillez sélectionner au moins un pays et un mois.")
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("Retour à l'accueil"):
            st.session_state.page = 'home'
        return
    
    filtered_df = df[df['Country'].isin(selected_countries) & df['Month'].isin(selected_months)]
    if filtered_df.empty:
        st.warning("Aucune donnée correspond aux filtres sélectionnés.")
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("Retour à l'accueil"):
            st.session_state.page = 'home'
        return
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("## Rapport des ventes par client et produit")
    
    customer_product_sales = filtered_df.groupby(['CustomerID', 'ProductName'])['QuantiteVendue'].sum().reset_index()
    customer_ids = sorted(customer_product_sales['CustomerID'].unique())
    selected_customers = st.multiselect(
        "Sélectionner des clients",
        options=customer_ids,
        default=customer_ids[:5] if len(customer_ids) >= 5 else customer_ids
    )
    
    filtered_table_data = customer_product_sales[customer_product_sales['CustomerID'].isin(selected_customers)]
    if not filtered_table_data.empty:
        st.dataframe(filtered_table_data, use_container_width=True)
        
        fig_table = go.Figure(data=[go.Table(
            header=dict(values=['ID Client', 'Nom du Produit', 'Quantité Achetée'],
                       fill_color='royalblue', align='left', font=dict(color='white', size=12)),
            cells=dict(values=[filtered_table_data['CustomerID'], filtered_table_data['ProductName'],
                             filtered_table_data['QuantiteVendue']],
                      fill_color='lavender', align='left')
        )])
        st.plotly_chart(fig_table, use_container_width=True)
        
        if st.button("Exporter en CSV"):
            csv = filtered_table_data.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="rapport_ventes.csv">Télécharger le fichier CSV</a>'
            st.markdown(href, unsafe_allow_html=True)
    else:
        st.warning("Aucune donnée disponible pour les clients sélectionnés.")
    
    if st.button("Retour à l'accueil"):
        st.session_state.page = 'home'
    st.markdown('</div>', unsafe_allow_html=True)

def page_dashboard():
    st.markdown('<div class="main-header"><h1>Dashboard</h1></div>', unsafe_allow_html=True)
    
    if 'data' not in st.session_state or st.session_state.data is None:
        st.error("Aucune donnée disponible. Veuillez importer un fichier de données valide dans 'Browse Files'.")
        if st.button("Retour à l'accueil"):
            st.session_state.page = 'home'
        return
    
    df = st.session_state.data
    st.sidebar.header("Filtres")
    countries = sorted(df['Country'].unique())
    selected_countries = st.sidebar.multiselect("Sélectionner des pays", options=countries, default=countries)
    months = sorted(df['Month'].unique(), key=lambda x: df[df['Month']==x]['MonthOrder'].iloc[0])
    selected_months = st.sidebar.multiselect("Sélectionner des mois", options=months, default=months)
    
    if not selected_countries or not selected_months:
        st.warning("Veuillez sélectionner au moins un pays et un mois.")
        if st.button("Retour à l'accueil"):
            st.session_state.page = 'home'
        return
    
    filtered_df = df[df['Country'].isin(selected_countries) & df['Month'].isin(selected_months)]
    if filtered_df.empty:
        st.warning("Aucune donnée correspond aux filtres sélectionnés.")
        if st.button("Retour à l'accueil"):
            st.session_state.page = 'home'
        return
    
    sales_by_month_country = filtered_df.groupby(['Country', 'Month', 'MonthOrder'])['MontantVentes'].sum().reset_index().sort_values('MonthOrder')
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Statistiques Globales")
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    total_sales = filtered_df['MontantVentes'].sum()
    total_quantity = filtered_df['QuantiteVendue'].sum()
    avg_sale_per_transaction = total_sales / len(filtered_df) if len(filtered_df) > 0 else 0
    num_customers = filtered_df['CustomerID'].nunique()
    
    metric_col1.metric("Ventes Totales", f"{total_sales:,.2f} €")
    metric_col2.metric("Quantité Totale Vendue", f"{total_quantity:,}")
    metric_col3.metric("Moyenne par Transaction", f"{avg_sale_per_transaction:.2f} €")
    metric_col4.metric("Nombre de Clients", f"{num_customers}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Ventes par Pays", "Ventes Mensuelles", "Ventes par Produit", "Répartition par Pays"])
    
    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("Ventes totales par pays et par mois")
        fig1 = px.bar(sales_by_month_country, x='Month', y='MontantVentes', color='Country', barmode='group',
                     labels={'MontantVentes': 'Ventes Totales', 'Month': 'Mois', 'Country': 'Pays'},
                     category_orders={"Month": months})
        fig1.update_layout(xaxis_title="Mois", yaxis_title="Ventes Totales", legend_title="Pays", height=600)
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("Ventes totales par mois pour chaque pays")
        fig2 = go.Figure()
        for country in sales_by_month_country['Country'].unique():
            country_data = sales_by_month_country[sales_by_month_country['Country'] == country]
            fig2.add_trace(go.Bar(x=country_data['Month'], y=country_data['MontantVentes'], name=country))
        fig2.update_layout(barmode='stack', xaxis_title='Mois', yaxis_title='Ventes Totales',
                          xaxis={'categoryorder':'array', 'categoryarray': months}, height=600)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("Ventes totales par produit")
        product_sales = filtered_df.groupby('ProductName')['MontantVentes'].sum().sort_values(ascending=False).reset_index()
        top_products = product_sales.head(10)
        fig3 = px.bar(top_products, x='ProductName', y='MontantVentes',
                     labels={'MontantVentes': 'Ventes Totales', 'ProductName': 'Produit'},
                     color='MontantVentes', color_continuous_scale='Viridis')
        fig3.update_layout(xaxis_title='Produit', yaxis_title='Ventes Totales', height=600)
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("Répartition des ventes mensuelles par pays")
        country_totals = sales_by_month_country.groupby('Country')['MontantVentes'].sum().to_dict()
        col1, col2 = st.columns(2)
        countries_list = sorted(sales_by_month_country['Country'].unique())
        half = len(countries_list) // 2 + len(countries_list) % 2
        
        for i, country in enumerate(countries_list):
            current_col = col1 if i < half else col2
            country_data = sales_by_month_country[sales_by_month_country['Country'] == country]
            if country_data.empty or country not in country_totals:
                continue
            country_data['Percentage'] = country_data['MontantVentes'] / country_totals[country] * 100
            country_data['Labels'] = country_data.apply(
                lambda row: f"{row['Month']} ({row['Percentage']:.1f}%)", axis=1
            )
            fig = go.Figure(data=[go.Pie(
                labels=country_data['Labels'],
                values=country_data['MontantVentes'],
                hole=0.3,
                sort=False
            )])
            fig.update_layout(title=f"Ventes pour {country}", height=400)
            current_col.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("Retour à l'accueil"):
        st.session_state.page = 'home'

# Navigation
page_map = {
    'home': page_home,
    'browse_files': page_browse_files,
    'create_new': page_create_new,
    'manage_data': page_manage_data,
    'documentation': page_documentation,
    'analysis_report': page_analysis_report,
    'interactive_report': page_interactive_report,
    'dashboard': page_dashboard
}

if 'page' not in st.session_state:
    st.session_state.page = 'home'

if st.session_state.page in page_map:
    page_map[st.session_state.page]()
else:
    st.error(f"Page '{st.session_state.page}' non trouvée. Retour à l'accueil.")
    st.session_state.page = 'home'
    page_home()

# Ajouter un pied de page
st.markdown("""
<div class="footer">
    Système d'Analyse des Ventes © 2025
</div>
""", unsafe_allow_html=True)
