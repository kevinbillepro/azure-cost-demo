import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

# --------------------------
# 1. Données fictives (exemple Azure Advisor)
# --------------------------
data = [
    ["Cost", "VM sous-utilisée", "Réduire la taille à B2s", "Medium"],
    ["Security", "Port 3389 ouvert", "Restreindre avec NSG", "High"],
    ["HighAvailability", "VM sans redondance", "Activer Availability Set", "High"],
    ["Performance", "Base SQL surdimensionnée", "Réduire DTUs à 50", "Low"],
]

df = pd.DataFrame(data, columns=["Catégorie", "Problème", "Solution", "Impact"])

# --------------------------
# 2. Interface Streamlit
# --------------------------
st.title("☁️ Azure Advisor – Démo Rapport PDF")
st.write("Voici un exemple de rapport généré automatiquement à partir de recommandations Azure Advisor (données fictives).")

st.subheader("📊 Recommandations (exemple)")
st.dataframe(df)

# --------------------------
# 3. Graphique matplotlib
# --------------------------
fig, ax = plt.subplots()
df["Catégorie"].value_counts().plot(kind="bar", ax=ax, color="skyblue")
ax.set_title("Répartition par catégorie")
ax.set_ylabel("Nombre de recommandations")
st.pyplot(fig)

# --------------------------
# 4. Génération du PDF
# --------------------------
def generate_pdf(dataframe):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(150, 800, "Rapport d’optimisation Azure Advisor (Démo)")

    # Tableau
    table_data = [["Catégorie", "Problème", "Solution", "Impact"]] + dataframe.values.tolist()
    table = Table(table_data, colWidths=[100, 200, 200, 80])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#2E86C1")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("FONTSIZE", (0,0), (-1,-1), 8),
    ]))
    table.wrapOn(c, 50, 600)
    table.drawOn(c, 50, 600)

    c.setFont("Helvetica", 10)
    c.drawString(50, 580, f"Nombre total de recommandations : {len(dataframe)}")

    c.save()
    buffer.seek(0)
    return buffer

# Bouton téléchargement
pdf_bytes = generate_pdf(df)
st.download_button(
    label="📥 Télécharger le rapport PDF",
    data=pdf_bytes,
    file_name="azure_advisor_report_demo.pdf",
    mime="application/pdf"
)
