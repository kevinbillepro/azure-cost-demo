import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

# Azure SDK
from azure.identity import ClientSecretCredential
from azure.mgmt.advisor import AdvisorManagementClient

# --------------------------
# 1. Connexion Azure via secrets
# --------------------------
tenant_id = st.secrets["AZURE_TENANT_ID"]
client_id = st.secrets["AZURE_CLIENT_ID"]
client_secret = st.secrets["AZURE_CLIENT_SECRET"]
subscription_id = st.secrets["AZURE_SUBSCRIPTION_ID"]

credential = ClientSecretCredential(
    tenant_id=tenant_id,
    client_id=client_id,
    client_secret=client_secret
)

client = AdvisorManagementClient(credential, subscription_id)

st.title("☁️ Azure Advisor – Rapport PDF")
st.write("Cette app récupère vos recommandations Azure Advisor et génère un PDF clair.")

# --------------------------
# 2. Récupération des recommandations
# --------------------------
recs = []
try:
    for rec in client.recommendations.list():
        recs.append([
            rec.category,
            rec.short_description.problem,
            rec.short_description.solution,
            rec.impact
        ])
except Exception as e:
    st.error(f"Erreur lors de la récupération des recommandations : {e}")
    st.stop()

if not recs:
    st.warning("✅ Aucune recommandation trouvée.")
    st.stop()

df = pd.DataFrame(recs, columns=["Catégorie", "Problème", "Solution", "Impact"])

# --------------------------
# 3. Affichage tableau
# --------------------------
st.subheader("📊 Recommandations Azure Advisor")
st.dataframe(df)

# --------------------------
# 4. Graphique matplotlib
# --------------------------
fig, ax = plt.subplots()
df["Catégorie"].value_counts().plot(kind="bar", ax=ax, color="skyblue")
ax.set_title("Répartition par catégorie")
ax.set_ylabel("Nombre de recommandations")
st.pyplot(fig)

# --------------------------
# 5. Génération PDF
# --------------------------
def generate_pdf(dataframe):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(120, 800, "Rapport d’optimisation Azure Advisor")

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

pdf_bytes = generate_pdf(df)

st.download_button(
    label="📥 Télécharger le rapport PDF",
    data=pdf_bytes,
    file_name="azure_advisor_report.pdf",
    mime="application/pdf"
)
