import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import base64
from pathlib import Path
import os

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Système d'Analyse des Ventes",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Fonction pour ajouter image de fond et CSS personnalisé
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
def load_data():
    # Essayer de charger le fichier merged_data.csv
    file_path = "merged_data.csv"
    if not os.path.exists(file_path):
        st.error(f"Le fichier {file_path} n'a pas été trouvé. Veuillez télécharger vos données dans la section 'Browse Files'.")
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(file_path)
        st.success(f"Données chargées avec succès depuis {file_path}")
        
        # Vérification des colonnes nécessaires
        required_columns = ['Country', 'Month', 'CustomerID', 'ProductName', 'QuantiteVendue', 'MontantVentes']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"Erreur: Les colonnes suivantes sont manquantes dans votre fichier: {', '.join(missing_columns)}")
            return pd.DataFrame()
        
        # Si 'MonthOrder' n'existe pas, le créer
        if 'MonthOrder' not in df.columns:
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            month_order = {month: i for i, month in enumerate(months)}
            
            # Vérifier si les mois dans le df correspondent au format attendu
            if set(df['Month'].unique()).issubset(set(months)):
                df['MonthOrder'] = df['Month'].map(month_order)
            else:
                st.warning("Format des mois non reconnu. Ordre chronologique peut être incorrect.")
                # Assigner un ordre arbitraire basé sur l'ordre d'apparition
                unique_months = df['Month'].unique()
                custom_order = {month: i for i, month in enumerate(unique_months)}
                df['MonthOrder'] = df['Month'].map(custom_order)
        
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        return pd.DataFrame()

# Fonction pour télécharger un fichier et le sauvegarder
def save_uploaded_file(uploaded_file):
    try:
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return True
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde du fichier: {e}")
        return False

# Appliquer les styles
add_bg_and_styling()

# Définir les pages
def page_home():
    st.markdown('<div class="main-header"><h1>Système d\'Analyse des Ventes</h1></div>', unsafe_allow_html=True)
    
    # Disposition en 2 colonnes pour les boutons
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if st.button('Browse Files', key='btn_browse', help="Parcourir les fichiers de données", use_container_width=True):
            st.session_state.page = 'browse_files'
        if st.button('Create New', key='btn_create', help="Créer une nouvelle analyse", use_container_width=True):
            st.session_state.page = 'create_new'
        if st.button('Manage Data Sources', key='btn_manage', help="Gérer les sources de données", use_container_width=True):
            st.session_state.page = 'manage_data'
        if st.button('Documentation', key='btn_docs', help="Consulter la documentation", use_container_width=True):
            st.session_state.page = 'documentation'
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if st.button('Analysis Report', key='btn_analysis', help="Voir le rapport d'analyse", use_container_width=True):
            st.session_state.page = 'analysis_report'
        if st.button('Interactive Report', key='btn_interactive', help="Consulter le rapport interactif", use_container_width=True):
            st.session_state.page = 'interactive_report'
        if st.button('Dashboard', key='btn_dashboard', help="Afficher le tableau de bord", use_container_width=True):
            st.session_state.page = 'dashboard'
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Vidéo ou image introductive
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
    
    # Afficher le statut des données
    file_path = "merged_data.csv"
    if os.path.exists(file_path):
        st.success(f"Base de données détectée: {file_path}")
    else:
        st.warning("Aucune base de données détectée. Veuillez télécharger votre fichier dans la section 'Browse Files'.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def page_browse_files():
    st.markdown('<div class="main-header"><h1>Browse Files</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Téléchargez votre fichier de données", type=["csv", "xlsx", "xls"])
    
    if uploaded_file is not None:
        # Afficher les informations du fichier
        st.write(f"Nom du fichier: {uploaded_file.name}")
        st.write(f"Type du fichier: {uploaded_file.type}")
        st.write(f"Taille du fichier: {uploaded_file.size} bytes")
        
        # Option pour visualiser un aperçu des données
        if st.checkbox("Aperçu du fichier"):
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.write("Aperçu des données:")
                st.dataframe(df.head())
                
                # Afficher les statistiques des données
                st.write("Statistiques des données:")
                st.write(df.describe())
                
                # Afficher les colonnes
                st.write("Colonnes disponibles:")
                st.write(", ".join(df.columns.tolist()))
            except Exception as e:
                st.error(f"Erreur lors de la lecture du fichier: {e}")
        
        # Option pour sauvegarder le fichier
        if st.button("Utiliser ce fichier comme source de données"):
            if save_uploaded_file(uploaded_file):
                st.success(f"Fichier {uploaded_file.name} sauvegardé avec succès! Vous pouvez maintenant utiliser ces données dans les rapports.")
                # Si le fichier est sauvegardé avec un nom différent de merged_data.csv, le renommer
                if uploaded_file.name != "merged_data.csv":
                    try:
                        os.rename(uploaded_file.name, "merged_data.csv")
                        st.success("Fichier renommé en 'merged_data.csv' pour être utilisé par l'application.")
                    except Exception as e:
                        st.error(f"Erreur lors du renommage du fichier: {e}")
            else:
                st.error("Échec de sauvegarde du fichier.")
    
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
    
    # Afficher les fichiers disponibles
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
                        if file.endswith('.csv'):
                            df = pd.read_csv(file)
                        else:
                            df = pd.read_excel(file)
                        
                        st.session_state.preview_file = file
                        st.session_state.preview_df = df
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Erreur lors de la lecture du fichier: {e}")
            
            with col3:
                if st.button(f"Utiliser", key=f"use_{file}"):
                    if file != "merged_data.csv":
                        try:
                            # Si merged_data.csv existe déjà, le supprimer
                            if os.path.exists("merged_data.csv"):
                                os.remove("merged_data.csv")
                            
                            # Copier le fichier sélectionné en merged_data.csv
                            if file.endswith('.csv'):
                                df = pd.read_csv(file)
                            else:
                                df = pd.read_excel(file)
                            
                            df.to_csv("merged_data.csv", index=False)
                            st.success(f"Le fichier {file} est maintenant utilisé comme source de données principale.")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Erreur lors de la définition du fichier comme source principale: {e}")
                    else:
                        st.info("Ce fichier est déjà la source de données principale.")
    else:
        st.info("Aucun fichier de données disponible. Veuillez télécharger un fichier dans la section 'Browse Files'.")
    
    # Afficher l'aperçu du fichier si disponible
    if hasattr(st.session_state, 'preview_file') and hasattr(st.session_state, 'preview_df'):
        st.subheader(f"Aperçu de {st.session_state.preview_file}")
        st.dataframe(st.session_state.preview_df.head())
        
        # Afficher des informations supplémentaires
        st.write(f"Nombre total de lignes: {len(st.session_state.preview_df)}")
        st.write(f"Colonnes disponibles: {', '.join(st.session_state.preview_df.columns.tolist())}")
        
        # Option pour effacer l'aperçu
        if st.button("Fermer l'aperçu"):
            del st.session_state.preview_file
            del st.session_state.preview_df
            st.experimental_rerun()
    
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
    merged_df = load_data()
    
    if merged_df.empty:
        st.warning("Aucune donnée disponible. Veuillez charger un fichier de données valide.")
        return
    
    # Créer un rapport d'analyse
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("## Rapport d'analyse des ventes")
    
    # Statistiques globales
    total_sales = merged_df['MontantVentes'].sum()
    avg_sales = merged_df['MontantVentes'].mean()
    total_quantity = merged_df['QuantiteVendue'].sum()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Ventes Totales", f"{total_sales:,.2f} €")
    col2.metric("Vente Moyenne", f"{avg_sales:.2f} €")
    col3.metric("Quantité Totale", f"{total_quantity}")
    
    # Meilleurs pays
    st.write("### Top des pays par ventes")
    top_countries = merged_df.groupby('Country')['MontantVentes'].sum().sort_values(ascending=False).reset_index()
    st.dataframe(top_countries, use_container_width=True)
    
    # Évolution mensuelle
    st.write("### Évolution mensuelle des ventes")
    monthly_sales = merged_df.groupby(['Month', 'MonthOrder'])['MontantVentes'].sum().reset_index()
    monthly_sales = monthly_sales.sort_values('MonthOrder')
    
    fig = px.line(monthly_sales, x='Month', y='MontantVentes',
                 labels={'MontantVentes': 'Ventes Totales', 'Month': 'Mois'},
                 markers=True)
    
    fig.update_layout(
        xaxis_title="Mois", 
        yaxis_title="Ventes Totales",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Bouton de retour
    if st.button("Retour à l'accueil"):
        st.session_state.page = 'home'
    st.markdown('</div>', unsafe_allow_html=True)

def page_interactive_report():
    st.markdown('<div class="main-header"><h1>Interactive Report</h1></div>', unsafe_allow_html=True)
    
    # Charger les données
    merged_df = load_data()
    
    if merged_df.empty:
        st.warning("Aucune donnée disponible. Veuillez charger un fichier de données valide.")
        return
    
    # Filtres
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("## Filtres")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Filtre par pays
        countries = sorted(merged_df['Country'].unique())
        selected_countries = st.multiselect(
            "Sélectionner des pays",
            options=countries,
            default=countries
        )
    
    with col2:
        # Filtre par mois
        months = sorted(merged_df['Month'].unique(), key=lambda x: merged_df[merged_df['Month']==x]['MonthOrder'].iloc[0])
        selected_months = st.multiselect(
            "Sélectionner des mois",
            options=months,
            default=months
        )
    
    # Filtrer les données
    filtered_df = merged_df[
        (merged_df['Country'].isin(selected_countries)) &
        (merged_df['Month'].isin(selected_months))
    ]
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Rapport interactif
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("## Rapport des ventes par client et produit")
    
    # Grouper les données par client et produit
    customer_product_sales = filtered_df.groupby(['CustomerID', 'ProductName'])['QuantiteVendue'].sum().reset_index()
    
    # Ajouter un filtre pour les clients
    customer_ids = sorted(customer_product_sales['CustomerID'].unique())
    selected_customers = st.multiselect(
        "Sélectionner des clients",
        options=customer_ids,
        default=customer_ids[:5] if len(customer_ids) > 5 else customer_ids
    )
    
    # Filtrer les données du tableau
    filtered_table_data = customer_product_sales[customer_product_sales['CustomerID'].isin(selected_customers)]
    
    # Créer un tableau interactif
    if not filtered_table_data.empty:
        st.dataframe(filtered_table_data, use_container_width=True)
        
        fig_table = go.Figure(data=[go.Table(
            header=dict(
                values=['ID Client', 'Nom du Produit', 'Quantité Achetée'],
                fill_color='royalblue',
                align='left',
                font=dict(color='white', size=12)
            ),
            cells=dict(
                values=[
                    filtered_table_data['CustomerID'],
                    filtered_table_data['ProductName'],
                    filtered_table_data['QuantiteVendue']
                ],
                fill_color='lavender',
                align='left'
            )
        )])
        
        st.plotly_chart(fig_table, use_container_width=True)
    else:
        st.warning("Aucune donnée disponible pour les filtres sélectionnés")
    
    # Export button
    if st.button("Exporter en CSV"):
        csv = filtered_table_data.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="rapport_ventes.csv">Télécharger le fichier CSV</a>'
        st.markdown(href, unsafe_allow_html=True)
    
    # Bouton de retour
    if st.button("Retour à l'accueil"):
        st.session_state.page = 'home'
    st.markdown('</div>', unsafe_allow_html=True)

def page_dashboard():
    st.markdown('<div class="main-header"><h1>Dashboard</h1></div>', unsafe_allow_html=True)
    
    # Chargement des données
    merged_df = load_data()
    
    if merged_df.empty:
        st.warning("Aucune donnée disponible. Veuillez charger un fichier de données valide.")
        return
    
    # Sidebar avec filtre
    st.sidebar.header("Filtres")
    
    # Filtre par pays
    countries = sorted(merged_df['Country'].unique())
    selected_countries = st.sidebar.multiselect(
        "Sélectionner des pays",
        options=countries,
        default=countries
    )
    
    # Filtre par mois
    months = sorted(merged_df['Month'].unique(), key=lambda x: merged_df[merged_df['Month']==x]['MonthOrder'].iloc[0])
    selected_months = st.sidebar.multiselect(
        "Sélectionner des mois",
        options=months,
        default=months
    )
    
    # Filtrer les données
    filtered_df = merged_df[
        (merged_df['Country'].isin(selected_countries)) &
        (merged_df['Month'].isin(selected_months))
    ]
    
    # Créer des données agrégées pour les graphiques
    sales_by_month_country = filtered_df.groupby(['Country', 'Month', 'MonthOrder'])['MontantVentes'].sum().reset_index()
    sales_by_month_country = sales_by_month_country.sort_values('MonthOrder')
    
    # Statistiques récapitulatives
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Statistiques Globales")
    
    # Créer deux colonnes pour les métriques
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    # Calculer les métriques
    total_sales = filtered_df['MontantVentes'].sum()
    total_quantity = filtered_df['QuantiteVendue'].sum()
    avg_sale_per_transaction = total_sales / len(filtered_df) if len(filtered_df) > 0 else 0
    num_customers = filtered_df['CustomerID'].nunique()
    
    # Afficher les métriques
    metric_col1.metric("Ventes Totales", f"{total_sales:,.2f} €")
    metric_col2.metric("Quantité Totale Vendue", f"{total_quantity:,}")
    metric_col3.metric("Moyenne par Transaction", f"{avg_sale_per_transaction:.2f} €")
    metric_col4.metric("Nombre de Clients", f"{num_customers}")
    st.markdown('</div>', unsafe_allow_html=True)

    # Onglets pour les différents graphiques
    tab1, tab2, tab3, tab4 = st.tabs(["Ventes par Pays", "Ventes Mensuelles", "Ventes par Produit", "Répartition par Pays"])
    
    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("Ventes totales par pays et par mois")
        
        fig1 = px.bar(
            sales_by_month_country, 
            x='Month', 
            y='MontantVentes', 
            color='Country',
            barmode='group',
            labels={'MontantVentes': 'Ventes Totales', 'Month': 'Mois', 'Country': 'Pays'},
            category_orders={"Month": months}
        )
        
        fig1.update_layout(
            xaxis_title="Mois", 
            yaxis_title="Ventes Totales",
            legend_title="Pays",
            height=600
        )
        
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("Ventes totales par mois pour chaque pays")
        
        fig2 = go.Figure()
        
        for country in sales_by_month_country['Country'].unique():
            country_data = sales_by_month_country[sales_by_month_country['Country'] == country]
            fig2.add_trace(go.Bar(
                x=country_data['Month'],
                y=country_data['MontantVentes'],
                name=country
            ))
        
        fig2.update_layout(
            barmode='stack',
            xaxis_title='Mois',
            yaxis_title='Ventes Totales',
            xaxis={'categoryorder':'array', 'categoryarray': months},
            height=600
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("Ventes totales par produit")
        
        # Top produits par ventes
        product_sales = filtered_df.groupby('ProductName')['MontantVentes'].sum().sort_values(ascending=False).reset_index()
        top_products = product_sales.head(10)
        
        fig3 = px.bar(
            top_products,
            x='ProductName',
            y='MontantVentes',
            labels={'MontantVentes': 'Ventes Totales', 'ProductName': 'Produit'},
            color='MontantVentes',
            color_continuous_scale='Viridis'
        )
        
        fig3.update_layout(
            xaxis_title='Produit',
            yaxis_title='Ventes Totales',
            height=600
        )
        
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.header("Répartition des ventes mensuelles par pays")
        
        # Calculer les totaux par pays pour les pourcentages
        country_totals = sales_by_month_country.groupby('Country')['MontantVentes'].sum().to_dict()
        
        # Créer un conteneur pour les diagrammes en camembert
        col1, col2 = st.columns(2)
        
        countries_list = sorted(sales_by_month_country['Country'].unique())
        half = len(countries_list) // 2 + len(countries_list) % 2
        
        for i, country in enumerate(countries_list):
            current_col = col1 if i < half else col2
            
            country_data = sales_by_month_country[sales_by_month_country['Country'] == country]
            
            # Calculer les pourcentages
            country_data['Percentage'] = country_data['MontantVentes'] / country_totals[country] * 100
            
            # Ajouter des étiquettes avec les pourcentages
            country_data['Labels'] = country_data['Month'] + ' (' + country_data['Percentage'].round(1).astype(str) + '%)'
            
            fig = go.Figure(data=[go.Pie(
                labels=country_data['Labels'],
                values=country_data['MontantVentes'],
                hole=0.3,
                sort=False
            )])
            
            fig.update_layout(
                title=f"Ventes pour {country}",
                height=400
            )
            
            current_col.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Bouton de retour
    if st.button("Retour à l'accueil"):
        st.session_state.page = 'home'

# Navigation
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# Afficher la page actuelle
if st.session_state.page == 'home':
    page_home()
elif st.session_state.page == 'browse_files':
    page_browse_files()
elif st.session_state.page == 'create_new':
    page_create_new()
elif st.session_state.page == 'manage_data':
    page_manage_data()
elif st.session_state.page == 'documentation':
    page_documentation()
elif st.session_state.page == 'analysis_report':
    page_analysis_report()
elif st.session_state.page == 'interactive_report':
    page_interactive_report()
elif st.session_state.page == 'dashboard':
    page_dashboard()

# Ajouter un pied de page
st.markdown("""
<div class="footer">
    Système d'Analyse des Ventes © 2025
</div>
""", unsafe_allow_html=True)
