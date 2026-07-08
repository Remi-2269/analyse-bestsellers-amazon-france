# ============================================================
# Dashboard Amazon Best-Sellers France 2020-2026
# Objectif : générer les graphiques pour un portfolio GitHub
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


# ============================================================
# 1. CONFIGURATION
# ============================================================

DATA_PATH = "data/Data_amazon_bestsellers_france.xlsx"

OUTPUT_DIR = Path("outputs/figures")
TABLES_DIR = Path("outputs/tables")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams["figure.figsize"] = (12, 7)
plt.rcParams["font.size"] = 11


# ============================================================
# 2. CHARGEMENT ET PRÉPARATION DES DONNÉES
# ============================================================

def load_data(path: str) -> pd.DataFrame:
    """
    Charge le fichier Excel, renomme les colonnes utiles,
    nettoie les données et prépare le dataset pour les graphiques.
    """

    df = pd.read_excel(path)

    # Nettoyage des noms de colonnes
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.replace("\n", " ", regex=False)
    )

    print("Colonnes disponibles dans le fichier Excel :")
    print(df.columns.tolist())

    # Renommage des colonnes du fichier Excel
    rename_map = {
        "Classement": "classement",
        "Titre du livre": "titre",
        "Auteur": "auteur",

        "prix": "prix",
        "Prix": "prix",

        "Nombre d’avis": "avis",
        "Nombre d'avis": "avis",
        "Avis": "avis",
        "Reviews": "avis",

        "Note moyenne": "note",
        "Note": "note",

        "Nombre de pages": "pages",
        "Pages": "pages",
        "Length": "pages",

        "format": "format",
        "Format": "format",

        "Pays": "pays",

        "annee": "annee",
        "Année": "annee",
        "Année classement": "annee",
        "Année du classement": "annee",

        "Catégorie harmonisée": "categorie",
        "Catégorie principale": "categorie",
        "Catégorie": "categorie",

        "Star ou nouveau": "star_ou_nouveau",
        "Livre 2 fois dans le top": "livre_2_fois_top",
        "Livre 2 fois dans le top ": "livre_2_fois_top",
        "Nombre d'apparition de l'auteur (par livres différents)": "apparitions_auteur_livres_differents",
        "Nombre d'apparition de l'auteur (même livre peut être 2 fois dans le top)": "apparitions_auteur_total",
        "Date de publication": "date_publication",
        "Nationalité de l'auteur": "nationalite_auteur"
    }

    df = df.rename(columns=rename_map)

    # Colonnes indispensables pour les graphiques
    required_columns = [
        "annee",
        "categorie",
        "prix",
        "note",
        "avis",
        "pages",
        "format"
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(
            f"\nColonnes manquantes : {missing_columns}\n\n"
            f"Colonnes trouvées : {df.columns.tolist()}\n\n"
            "Il faut adapter le rename_map avec les vrais noms de colonnes Excel."
        )

    # Nettoyage spécial de l'année
    # Cette partie récupère correctement 2020, 2021, 2022... même si Excel lit la colonne comme date ou texte.
    df["annee"] = (
        df["annee"]
        .astype(str)
        .str.extract(r"(20[0-9]{2})")[0]
    )

    df["annee"] = pd.to_numeric(df["annee"], errors="coerce")

    # Nettoyage des autres colonnes numériques
    numeric_columns = ["classement", "prix", "note", "avis", "pages"]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", ".", regex=False)
                .str.replace("€", "", regex=False)
                .str.replace(" ", "", regex=False)
                .str.replace("\u202f", "", regex=False)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Nettoyage des colonnes texte
    text_columns = ["titre", "auteur", "categorie", "format", "pays"]

    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Suppression des lignes indispensables vides
    df = df.dropna(subset=["annee", "categorie"])

    # Année en entier
    df["annee"] = df["annee"].astype(int)

    # Suppression des catégories vides ou incorrectes
    df = df[df["categorie"].str.lower() != "nan"]

    print("\nAnnées détectées :")
    print(sorted(df["annee"].unique()))

    print("\nNombre de lignes après nettoyage :")
    print(len(df))

    return df


# ============================================================
# 3. FONCTIONS UTILITAIRES
# ============================================================

def save_chart(filename: str):
    """
    Sauvegarde le graphique dans outputs/figures.
    """

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=300, bbox_inches="tight")
    plt.close()


def add_vertical_bar_labels(ax):
    """
    Ajoute les valeurs au-dessus des barres verticales.
    """

    for container in ax.containers:
        ax.bar_label(container, padding=3)


def clean_filename(name: str) -> str:
    """
    Nettoie un texte pour l'utiliser comme nom de fichier.
    """

    return (
        name.lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("-", "_")
        .replace("é", "e")
        .replace("è", "e")
        .replace("ê", "e")
        .replace("à", "a")
        .replace("ç", "c")
    )


# ============================================================
# 4. KPI GLOBAUX
# ============================================================

def export_kpis(data: pd.DataFrame):
    """
    Calcule et exporte les KPI principaux.
    """

    kpis = {
        "Livres analysés": len(data),
        "Prix moyen": round(data["prix"].mean(), 2),
        "Note moyenne": round(data["note"].mean(), 2),
        "Avis moyens": round(data["avis"].mean(), 0),
        "Pages moyennes": round(data["pages"].mean(), 0)
    }

    kpi_df = pd.DataFrame(kpis.items(), columns=["Indicateur", "Valeur"])
    kpi_df.to_csv(TABLES_DIR / "kpis.csv", index=False)

    print("\nKPI principaux :")
    print(kpi_df)


# ============================================================
# 5. GRAPHIQUE : CATÉGORIES LES PLUS REPRÉSENTÉES
# ============================================================

def plot_categories_representees(data: pd.DataFrame):
    """
    Graphique horizontal des catégories les plus représentées.
    """

    category_counts = (
        data["categorie"]
        .value_counts()
        .sort_values(ascending=True)
    )

    fig, ax = plt.subplots(figsize=(12, 7))

    ax.barh(category_counts.index, category_counts.values)

    ax.set_title("Catégories les plus représentées", fontsize=16, weight="bold")
    ax.set_xlabel("Nombre de livres")
    ax.set_ylabel("Catégorie")

    for i, value in enumerate(category_counts.values):
        ax.text(value + 1, i, str(value), va="center")

    save_chart("01_categories_les_plus_representees.png")


# ============================================================
# 6. GRAPHIQUE : RÉPARTITION PAR TRANCHE DE PRIX
# ============================================================

def plot_repartition_prix(data: pd.DataFrame):
    """
    Répartition des livres par tranche de prix.
    """

    bins = [0, 10, 15, 20, np.inf]
    labels = ["Moins de 10 €", "10 € à 15 €", "15 € à 20 €", "20 € et plus"]

    data = data.copy()
    data["tranche_prix"] = pd.cut(
        data["prix"],
        bins=bins,
        labels=labels,
        right=False
    )

    price_counts = data["tranche_prix"].value_counts().reindex(labels)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.bar(price_counts.index, price_counts.values)

    ax.set_title("Répartition des livres par tranche de prix", fontsize=16, weight="bold")
    ax.set_xlabel("Tranche de prix")
    ax.set_ylabel("Nombre de livres")

    add_vertical_bar_labels(ax)

    save_chart("02_repartition_tranches_prix.png")


# ============================================================
# 7. GRAPHIQUE : HEATMAP CATÉGORIE / ANNÉE
# ============================================================

def plot_heatmap_categorie_annee(data: pd.DataFrame):
    """
    Heatmap du nombre de livres par catégorie et par année.
    """

    pivot = pd.pivot_table(
        data,
        index="annee",
        columns="categorie",
        values="titre" if "titre" in data.columns else "format",
        aggfunc="count",
        fill_value=0
    )

    pivot = pivot.sort_index(ascending=False)

    fig, ax = plt.subplots(figsize=(14, 7))

    im = ax.imshow(pivot.values, aspect="auto")

    ax.set_title("Nombre de livres par catégorie et par année", fontsize=16, weight="bold")
    ax.set_xlabel("Catégorie")
    ax.set_ylabel("Année")

    ax.set_xticks(np.arange(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=35, ha="right")

    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_yticklabels(pivot.index.astype(int))

    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            value = pivot.iloc[i, j]
            ax.text(j, i, value, ha="center", va="center")

    fig.colorbar(im, ax=ax, label="Nombre de livres")

    pivot.to_csv(TABLES_DIR / "categories_par_annee.csv")

    save_chart("03_heatmap_categories_annees.png")


# ============================================================
# 8. GRAPHIQUE : ÉVOLUTION DES 3 PRINCIPALES CATÉGORIES
# ============================================================

def plot_evolution_top_categories(data: pd.DataFrame, top_n: int = 3):
    """
    Évolution annuelle des 3 catégories les plus représentées.
    """

    top_categories = (
        data["categorie"]
        .value_counts()
        .head(top_n)
        .index
        .tolist()
    )

    evolution = (
        data[data["categorie"].isin(top_categories)]
        .groupby(["annee", "categorie"])
        .size()
        .reset_index(name="nombre_livres")
    )

    pivot = evolution.pivot(
        index="annee",
        columns="categorie",
        values="nombre_livres"
    ).fillna(0)

    fig, ax = plt.subplots(figsize=(12, 7))

    for category in pivot.columns:
        ax.plot(
            pivot.index,
            pivot[category],
            marker="o",
            linewidth=2,
            label=category
        )

        for x, y in zip(pivot.index, pivot[category]):
            ax.text(x, y + 0.5, int(y), ha="center")

    ax.set_title("Évolution des 3 principales catégories du Top 100", fontsize=16, weight="bold")
    ax.set_xlabel("Année")
    ax.set_ylabel("Nombre de livres")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    save_chart("04_evolution_top_3_categories.png")


# ============================================================
# 9. GRAPHIQUE : RÉPARTITION DES FORMATS
# ============================================================

def plot_repartition_formats(data: pd.DataFrame):
    """
    Répartition des formats des livres.
    """

    format_counts = (
        data["format"]
        .value_counts()
        .sort_values(ascending=False)
    )

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.bar(format_counts.index, format_counts.values)

    ax.set_title("Répartition des formats des livres du Top 100", fontsize=16, weight="bold")
    ax.set_xlabel("Format")
    ax.set_ylabel("Nombre de livres")

    add_vertical_bar_labels(ax)

    save_chart("05_repartition_formats.png")


# ============================================================
# 10. GRAPHIQUE : PRIX MOYEN PAR CATÉGORIE
# ============================================================

def plot_prix_moyen_par_categorie(data: pd.DataFrame):
    """
    Prix moyen par catégorie.
    """

    prix_moyen = (
        data
        .groupby("categorie")["prix"]
        .mean()
        .sort_values(ascending=True)
    )

    fig, ax = plt.subplots(figsize=(12, 7))

    ax.barh(prix_moyen.index, prix_moyen.values)

    ax.set_title("Prix moyen par catégorie", fontsize=16, weight="bold")
    ax.set_xlabel("Prix moyen (€)")
    ax.set_ylabel("Catégorie")

    for i, value in enumerate(prix_moyen.values):
        ax.text(value + 0.1, i, f"{value:.2f} €", va="center")

    save_chart("06_prix_moyen_par_categorie.png")


# ============================================================
# 11. GRAPHIQUE : NOTE MOYENNE PAR CATÉGORIE
# ============================================================

def plot_note_moyenne_par_categorie(data: pd.DataFrame):
    """
    Note moyenne par catégorie.
    """

    note_moyenne = (
        data
        .groupby("categorie")["note"]
        .mean()
        .sort_values(ascending=True)
    )

    fig, ax = plt.subplots(figsize=(12, 7))

    ax.barh(note_moyenne.index, note_moyenne.values)

    ax.set_title("Note moyenne par catégorie", fontsize=16, weight="bold")
    ax.set_xlabel("Note moyenne")
    ax.set_ylabel("Catégorie")
    ax.set_xlim(0, 5)

    for i, value in enumerate(note_moyenne.values):
        ax.text(value + 0.03, i, f"{value:.2f}", va="center")

    save_chart("07_note_moyenne_par_categorie.png")


# ============================================================
# 12. GRAPHIQUE : NOMBRE MOYEN D'AVIS PAR CATÉGORIE
# ============================================================

def plot_avis_moyens_par_categorie(data: pd.DataFrame):
    """
    Nombre moyen d'avis par catégorie.
    """

    avis_moyens = (
        data
        .groupby("categorie")["avis"]
        .mean()
        .sort_values(ascending=True)
    )

    fig, ax = plt.subplots(figsize=(12, 7))

    ax.barh(avis_moyens.index, avis_moyens.values)

    ax.set_title("Nombre moyen d'avis par catégorie", fontsize=16, weight="bold")
    ax.set_xlabel("Nombre moyen d'avis")
    ax.set_ylabel("Catégorie")

    for i, value in enumerate(avis_moyens.values):
        ax.text(value + 10, i, f"{value:.0f}", va="center")

    save_chart("08_avis_moyens_par_categorie.png")


# ============================================================
# 13. GRAPHIQUE : CORRÉLATION NOTE / CLASSEMENT
# ============================================================

def plot_correlation_note_classement(data: pd.DataFrame):
    """
    Nuage de points entre la note moyenne et le classement.
    """

    if "classement" not in data.columns:
        print("Colonne classement absente : graphique de corrélation ignoré.")
        return

    clean_data = data[["note", "classement"]].dropna()

    if clean_data.empty:
        print("Données insuffisantes pour la corrélation note / classement.")
        return

    correlation = clean_data["note"].corr(clean_data["classement"])

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.scatter(clean_data["note"], clean_data["classement"], alpha=0.6)

    ax.set_title(
        f"Relation entre note moyenne et classement\nCorrélation : {correlation:.2f}",
        fontsize=16,
        weight="bold"
    )

    ax.set_xlabel("Note moyenne")
    ax.set_ylabel("Classement")
    ax.grid(axis="both", alpha=0.3)

    save_chart("09_correlation_note_classement.png")


# ============================================================
# 14. EXPORT DES TABLEAUX AGRÉGÉS
# ============================================================

def export_summary_tables(data: pd.DataFrame):
    """
    Exporte les tableaux utilisés pour les graphiques.
    """

    categories_counts = (
        data["categorie"]
        .value_counts()
        .reset_index()
    )

    categories_counts.columns = ["categorie", "nombre_livres"]
    categories_counts.to_csv(TABLES_DIR / "categories_counts.csv", index=False)

    formats_counts = (
        data["format"]
        .value_counts()
        .reset_index()
    )

    formats_counts.columns = ["format", "nombre_livres"]
    formats_counts.to_csv(TABLES_DIR / "formats_counts.csv", index=False)

    resume_par_categorie = (
        data
        .groupby("categorie")
        .agg(
            nombre_livres=("categorie", "count"),
            prix_moyen=("prix", "mean"),
            note_moyenne=("note", "mean"),
            avis_moyens=("avis", "mean"),
            pages_moyennes=("pages", "mean")
        )
        .round(2)
        .reset_index()
    )

    resume_par_categorie.to_csv(TABLES_DIR / "resume_par_categorie.csv", index=False)


# ============================================================
# 15. EXÉCUTION DU SCRIPT
# ============================================================

if __name__ == "__main__":

    print("Début de la génération du dashboard...")

    df = load_data(DATA_PATH)

    export_kpis(df)

    plot_categories_representees(df)
    plot_repartition_prix(df)
    plot_heatmap_categorie_annee(df)
    plot_evolution_top_categories(df)
    plot_repartition_formats(df)
    plot_prix_moyen_par_categorie(df)
    plot_note_moyenne_par_categorie(df)
    plot_avis_moyens_par_categorie(df)
    plot_correlation_note_classement(df)

    export_summary_tables(df)

    print("\nGraphiques générés dans : outputs/figures/")
    print("Tableaux générés dans : outputs/tables/")
    print("Terminé.")