# Fonction pour charger les données
@st.cache_data
def load_data(uploaded_file=None):
    try:
        if uploaded_file is not None:
            # Charger les données depuis le fichier uploadé
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file)
            else:
                st.error("Format de fichier non supporté. Veuillez utiliser CSV ou Excel.")
                return None
        else:
            # Charger un fichier par défaut pour les tests (à remplacer par vos données)
            st.warning("Aucun fichier uploadé. Utilisation des données par défaut.")
            df = pd.read_csv('votre_fichier.csv')  # Remplacer par un chemin valide

        # Vérifier les colonnes requises
        required_columns = ['Country', 'Month', 'CustomerID', 'ProductName', 'QuantiteVendue', 'MontantVentes']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Colonnes manquantes dans les données : {', '.join(missing_columns)}")
            return None

        # Vérifier les types de données
        if not pd.api.types.is_numeric_dtype(df['MontantVentes']):
            st.error("La colonne 'MontantVentes' doit contenir des valeurs numériques.")
            return None
        if not pd.api.types.is_numeric_dtype(df['QuantiteVendue']):
            st.error("La colonne 'QuantiteVendue' doit contenir des valeurs numériques.")
            return None

        # Ajouter MonthOrder si absent
        if 'MonthOrder' not in df.columns:
            month_mapping = {
                'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
                'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
            }
            df['MonthOrder'] = df['Month'].map(month_mapping)
            if df['MonthOrder'].isna().any():
                st.error("Certains mois dans la colonne 'Month' ne sont pas reconnus. Valeurs attendues : January, February, etc.")
                return None

        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {str(e)}")
        return None

# Modification de page_browse_files pour intégrer le chargement de fichier
def page_browse_files():
    st.markdown('<div class="main-header"><h1>Browse Files</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Téléchargez vos fichiers de données", type=["csv", "xlsx", "xls"])
    
    if uploaded_file is not None:
        # Charger les données uploadées
        merged_df = load_data(uploaded_file)
        if merged_df is not None:
            st.success("Fichier chargé avec succès !")
            # Stocker les données dans la session pour les autres pages
            st.session_state['data'] = merged_df
            st.dataframe(merged_df.head(), use_container_width=True)  # Aperçu des données
    
    st.markdown("Cette section vous permet de parcourir et de télécharger vos fichiers de données pour analyse.")
    if st.button("Retour à l'accueil"):
        st.session_state.page = 'home'
    st.markdown('</div>', unsafe_allow_html=True)

# Modification des fonctions utilisant les données pour utiliser st.session_state['data']
def page_analysis_report():
    st.markdown('<div class="main-header"><h1>Analysis Report</h1></div>', unsafe_allow_html=True)
    
    # Vérifier si les données sont disponibles
    if 'data' not in st.session_state or st.session_state['data'] is None:
        st.error("Aucune donnée chargée. Veuillez uploader un fichier dans 'Browse Files'.")
        return
    
    merged_df = st.session_state['data']
    
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

# Modification de page_interactive_report
def page_interactive_report():
    st.markdown('<div class="main-header"><h1>Interactive Report</h1></div>', unsafe_allow_html=True)
    
    # Vérifier si les données sont disponibles
    if 'data' not in st.session_state or st.session_state['data'] is None:
        st.error("Aucune donnée chargée. Veuillez uploader un fichier dans 'Browse Files'.")
        return
    
    merged_df = st.session_state['data']
    
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
            default=countries if countries else []
        )
    
    with col2:
        # Filtre par mois
        months = sorted(merged_df['Month'].unique(), key=lambda x: merged_df[merged_df['Month']==x]['MonthOrder'].iloc[0])
        selected_months = st.multiselect(
            "Sélectionner des mois",
            options=months,
            default=months if months else []
        )
    
    # Vérifier si des filtres sont sélectionnés
    if not selected_countries or not selected_months:
        st.warning("Veuillez sélectionner au moins un pays et un mois.")
        return
    
    # Filtrer les données
    filtered_df = merged_df[
        (merged_df['Country'].isin(selected_countries)) &
        (merged_df['Month'].isin(selected_months))
    ]
    
    if filtered_df.empty:
        st.warning("Aucune donnée correspond aux filtres sélectionnés.")
        return
    
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
        default=customer_ids[:5] if len(customer_ids) >= 5 else customer_ids
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
        st.warning("Aucune donnée disponible pour les clients sélectionnés.")
    
    # Export button
    if not filtered_table_data.empty and st.button("Exporter en CSV"):
        csv = filtered_table_data.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="rapport_ventes.csv">Télécharger le fichier CSV</a>'
        st.markdown(href, unsafe_allow_html=True)
    
    # Bouton de retour
    if st.button("Retour à l'accueil"):
        st.session_state.page = 'home'
    st.markdown('</div>', unsafe_allow_html=True)

# Navigation
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# Liste des pages valides
valid_pages = [
    'home', 'browse_files', 'create_new', 'manage_data',
    'documentation', 'analysis_report', 'interactive_report', 'dashboard'
]

# Afficher la page actuelle
if st.session_state.page in valid_pages:
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
else:
    st.error(f"Page '{st.session_state.page}' non trouvée. Retour à l'accueil.")
    st.session_state.page = 'home'
    page_home()
