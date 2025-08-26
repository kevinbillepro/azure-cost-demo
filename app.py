import streamlit as st
import pandas as pd
from azure.identity import ClientSecretCredential
from azure.mgmt.advisor import AdvisorManagementClient
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

st.title("Azure Advisor – Multi-subscriptions avec Resource Group")

# 1. Connexion Azure via secrets
# --------------------------
tenant_id = st.secrets["AZURE_TENANT_ID"]
client_id = st.secrets["AZURE_CLIENT_ID"]
client_secret = st.secrets["AZURE_CLIENT_SECRET"]

credential = ClientSecretCredential(
    tenant_id=tenant_id,
    client_id=client_id,
    client_secret=client_secret
)

# Récupérer toutes les subscriptions accessibles
sub_client = SubscriptionClient(credential)
subscriptions = list(sub_client.subscriptions.list())

subscription_dict = {sub.display_name: sub.subscription_id for sub in subscriptions}

st.title("☁️ Azure Advisor – Multi-Subscription PDF")
st.write("Sélectionnez une subscription et générez un rapport PDF avec les recommandations Azure Advisor.")

# Dropdown pour choisir la subscription
selected_name = st.selectbox("Choisir une subscription :", list(subscription_dict.keys()))
subscription_id = subscription_dict[selected_name]
            all_recs = []

            # 🔄 Boucle sur chaque subscription
            for sub_id in subs_input.strip().splitlines():
                advisor_client = AdvisorManagementClient(credential, sub_id)

                for rec in advisor_client.recommendations.list():
                    # Récupérer le resource group si dispo
                    resource_group = getattr(getattr(rec, "resource_metadata", None), "resource_group", "N/A")

                    all_recs.append([
                        sub_id,
                        rec.category,
                        rec.short_description.problem,
                        rec.short_description.solution,
                        rec.impact,
                        resource_group
                    ])

            # 📊 DataFrame avec Resource Group
            df = pd.DataFrame(all_recs, columns=["Subscription", "Catégorie", "Problème", "Solution", "Impact", "Resource Group"])

            st.subheader("Recommandations Azure Advisor")
            st.dataframe(df)

            # Graphique : nombre de recos par resource group
            fig, ax = plt.subplots()
            df.groupby("Resource Group").size().sort_values(ascending=False).head(10).plot(kind="bar", ax=ax)
            ax.set_ylabel("Nombre de recommandations")
            ax.set_title("Top Resource Groups avec le plus de recommandations")
            st.pyplot(fig)

            # 📄 Génération PDF
            def generate_pdf(df):
                buffer = BytesIO()
                c = canvas.Canvas(buffer, pagesize=A4)
                c.setFont("Helvetica-Bold", 16)
                c.drawString(80, 800, "Rapport Azure Advisor – Multi-subscriptions")
                c.setFont("Helvetica", 12)

                # Tableau
                table_data = [df.columns.tolist()] + df.values.tolist()
                table = Table(table_data, colWidths=[80,80,140,140,60,80])
                table.setStyle(TableStyle([
                    ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#2E86C1")),
                    ("TEXTCOLOR",(0,0),(-1,0),colors.white),
                    ("ALIGN",(0,0),(-1,-1),"CENTER"),
                    ("GRID",(0,0),(-1,-1),0.25,colors.grey),
                    ("FONTSIZE",(0,0),(-1,-1),6)
                ]))
                table.wrapOn(c,50,600)
                table.drawOn(c,50,600)

                # Résumé
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50,560,f"Nombre total de recommandations : {len(df)}")
                c.drawString(50,540,f"Nombre de Resource Groups impactés : {df['Resource Group'].nunique()}")

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

    except Exception as e:
        st.error(f"Erreur : {e}")
