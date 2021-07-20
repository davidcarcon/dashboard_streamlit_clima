import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

image = Image.open('./cloud_mx.png')
df = pd.read_csv('datos/tuits_sentiment_all.csv', sep='\t')
df = df[["usuario", "tuit_es", "emoji"]]
df_can = pd.read_csv('datos/para_muestra.csv')

titulo = st.beta_container()
with titulo:
    st.title("Tweet's medio ambiente")

wordcl = st.beta_container()
with wordcl:
    st.image(image, width=600)

scatter = st.beta_container()
with scatter:
    fig = px.scatter(
        x=df_can["username"],
        y=df_can["promedio_sentiment"],
        color=df_can["PARTIDO_COALICION"]
    )
    fig.update_layout(
        xaxis_title="Usuario_twitter",
        yaxis_title="Promedio",
    )
    st.write(fig)
    
por_partido = st.beta_container()
with por_partido:
    partidos = df_can.PARTIDO_COALICION.unique()
    partido = st.selectbox("Elegir partido", options=partidos)
    df_partido = df_can[df_can.PARTIDO_COALICION == partido]
    salida = {
        'Partido_Coalicion': [partido],
        'Num_Candidatos': [df_partido.shape[0]],
        'Calificación_Promedio_Sentiment': [df_partido.promedio_sentiment.median()]
    }
    df_salida = pd.DataFrame(salida)
    st.table(df_salida)
    candidatos_par = df_partido.NOMBRE_CANDIDATO.unique()
    candidato = st.selectbox('Elegir candidato', options=candidatos_par)
    df_candidato = df_can[df_can.NOMBRE_CANDIDATO == candidato]
    st.table(df_candidato[['PARTIDO_COALICION', 'NOMBRE_CANDIDATO', 'promedio_sentiment', 'description', 'followers_count']])

newFeatures = st.beta_container()
with newFeatures:
    st.markdown("""
    #### Muestra de tweets con su analisis de sentimiento donde
    * :smile: es positivo
    * :no_mouth: es neutro
    * :angry: es negativo
    """)
    sentimiento = st.selectbox("Elegir el sentimiento", options=['\U0001F600', '\U0001F610', '\U0001F620'])
    st.table(df[df.emoji == sentimiento].sample(15))
    submit = st.button('Guardar')
    if submit:
        df.to_excel("descargas/sentiment_clima_usuarios_twitter.xlsx", sheet_name='sentiment', index=False)

st.markdown("""<style>
.main {
background-color: #AF9EC;
}</style>""", unsafe_allow_html=True )
