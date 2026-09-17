import base64
import io
import requests
from PIL import Image
import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Diagnostic de Plats Congolais",
    page_icon="🍲",
    layout="centered"
)

st.title("🍲 Diagnostic de Plats Congolais")
st.write("Téléversez une photo de votre plat pour l'analyser avec l'IA Gemini.")

# Récupération de la clé API depuis les secrets Streamlit
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    st.error("La clé API 'GEMINI_API_KEY' n'est pas configurée dans les Secrets de Streamlit.")
    st.stop()

# Sélecteur d'image
uploaded_file = st.file_uploader("Choisissez une photo de plat...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Aperçu de l'image", use_container_width=True)
    
    if st.button("Diagnostiquer le plat", type="primary"):
        with st.spinner("Analyse en cours par l'IA..."):
            # Conversion de l'image en base64
            buffered = io.BytesIO()
            image_format = image.format if image.format else "JPEG"
            image.save(buffered, format=image_format)
            base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

            prompt = """
            Examine cette photo de nourriture. S'agit-il d'un plat traditionnel de la République Démocratique du Congo (RDC) ?
            Si oui :
            1. Donne le nom exact du plat (ex: Madesu, Pondu, Fumbwa, Makayabu, Liboke, etc.).
            2. Donne un pourcentage de certitude/confiance.
            3. Liste les ingrédients principaux visibles ou probables dans la préparation.
            4. Donne une brève description du plat.
            
            Si ce n'est pas un plat congolais ou si ce n'est pas de la nourriture, indique-le clairement.
            Sois précis et réponds en français.
            """

            # Modèle officiel à jour
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"

            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": f"image/{image_format.lower()}",
                                "data": base64_image
                            }
                        }
                    ]
                }]
            }

            try:
                response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
                res_data = response.json()

                if "candidates" in res_data:
                    texte_reponse = res_data["candidates"][0]["content"]["parts"][0]["text"]
                    st.success("Diagnostic terminé !")
                    st.markdown(texte_reponse)
                else:
                    st.error("Erreur lors du traitement par l'API.")
                    st.json(res_data)

            except Exception as e:
                st.error(f"Erreur de connexion : {e}")
