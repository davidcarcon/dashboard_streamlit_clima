import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import nltk
import re
import networkx as nx
import matplotlib.pyplot as plt
nltk.download('punkt')



df_can = pd.read_csv('datos/datos_ult_dash.csv')
df_score = pd.read_csv('datos/score_users.csv')
df_score_v = df_score[['NOMBRE_CANDIDATO', 'ENTIDAD', 'PARTIDO_COALICION', 'Numero_tuits', 'score']]
df_score_v = df_score_v.rename(columns={'NOMBRE_CANDIDATO': 'Nombre del Candidato', 'ENTIDAD': 'Entidad',
                                        'PARTIDO_COALICION': 'Partido o Coalicón', 'Numero_tuits': 'Número de Tuits',
                                        'score': 'Score'})
stopwords = open('datos/spanish.txt')
stopwords = set(map(lambda x: x.replace('\n', ''), stopwords.readlines()))

dict_colores = {
    'JUNTOS HACEMOS HISTORIO': '#8C2F1A',
    'VA POR MEXICO': '#44DAD5',
    'MOVIMIENTO CIUDADANO': '#ED8F0F',
    'PARTIDO ACCIÓN NACIONAL': '#0C5FAD',
    'MORENA': '#8A3B3B',
    'PARTIDO DEL TRABAJO': '#F93409',
    'FUERZA POR MÉXICO': '#FD01EA',
    'PARTIDO VERDE ECOLOGISTA DE MÉXICO': '#00FF0B',
    'PARTIDO REVOLUCIONARIO INSTITUCIONAL': '#3D9E41',
    'PARTIDO DE LA REVOLUCIÓN DEMOCRÁTICA': '#FAF41E',
    'REDES SOCIALES PROGRESISTAS': '#FF0000',
    'PARTIDO ENCUENTRO SOLIDARIO': '#9B59B6'
}

partidos = ["Todos"] + list(df_can.PARTIDO_COALICION.unique())

#### Barra lateral
st.sidebar.markdown("## Partidos político")

select_event = st.sidebar.radio('Selecciona para obtener información', partidos)
#### Barra lateral

titulo = st.beta_container()
with titulo:
    st.title("Tweet's medio ambiente {}".format(select_event))

wordcl = st.beta_container()
with wordcl:
    if select_event == 'Todos':
        image =Image.open('nubes/cloud_mx.png')
        st.image(image, width=600)
    else:
        image = Image.open('nubes/cloud_mx_{}.png'.format(select_event))
        st.image(image, width=600)


bar = st.beta_container()
with bar:
    if select_event == 'Todos':
        s = df_can.PARTIDO_COALICION.value_counts().sort_values()
        y = df_can.groupby('PARTIDO_COALICION')['NOMBRE_CANDIDATO'].nunique().sort_values()
        st.header('Tuits hechos por cada Partido o Coalición')
        fig = px.bar(x=s.values, y=s.index, orientation='h',
                     labels={
                         "x": "Número de Tuits por Partido o Coalición",
                         "y": "Partido o Coalición"
                     }, color=dict_colores)
        fig.update_traces(showlegend=False)
        st.write(fig)
        st.header('Candidatos que hablan del clima por Partido o Coalición')
        fig2 = px.bar(x=y.values, y=y.index, orientation='h',
                     labels={
                         "x": "Número de Candidatos por Partido o Coalición",
                         "y": "Partido o Coalición"
                     }, color=dict_colores)
        fig2.update_traces(showlegend=False)
        st.write(fig2)

        st.header('Score generado por el número de tuits de cada candidato')
        st.table(df_score_v.head(15).assign(hack='').set_index('hack'))
    else:
        st.header('Muestra de Tuits hechos por candidatos del partido')
        df_partido = df_can[df_can['PARTIDO_COALICION'] == select_event]
        textos = df_partido.sample(5)['Texto_tuit'].to_frame().assign(hack='').set_index('hack')
        st.table(textos)

        st.header('Candidatos con mayor número de followers del Partido o Coalición')
        df_usuarios = df_can[df_can['PARTIDO_COALICION'] == select_event]
        max_follow = df_usuarios[['NOMBRE_CANDIDATO', 'username', 'description', 'followers_count']].drop_duplicates()
        max_follow['followers_count'] = max_follow['followers_count'].astype('int')
        max_follow = max_follow.sort_values(by='followers_count', ascending=False)
        max_follow = max_follow.head(5).assign(hack='').set_index('hack')
        st.table(max_follow)

        st.header('Palabras al rededor')
        cuerpo = " ".join(df_usuarios.Texto_tuit.to_list())
        cuerpo = cuerpo.lower()
        cuerpo = cuerpo.split()
        new_cuerpo = []
        for palabra in cuerpo:
            if not palabra in stopwords:
                new_cuerpo.append(palabra)
        new_cuerpo = " ".join(new_cuerpo)
        new_cuerpo = re.sub(r'[^\w\s]', '', new_cuerpo)
        tokens = nltk.word_tokenize(new_cuerpo)
        bgs = nltk.bigrams(tokens)
        fdist = nltk.FreqDist(bgs)
        buscar = []
        for k,v in fdist.items():
            if (k[0] == 'climático') or (k[1] == 'climático'):
                buscar.append(k[0])
                buscar.append(k[1])
        d = set(buscar)
        para_grafo = []
        for k,v in fdist.items():
            if (k[0] in d) or (k[1] in d):
                para_grafo.append(k)
        G = nx.Graph()
        G.add_edges_from(para_grafo[:10])
        options = {
            'font_size': '5',
            'node_color': 'white',
            'node_size': 2000,
            'width': 1
        }
        #dot = nx.nx_pydot.to_pydot(G)
        fig, ax = plt.subplots()
        ax = nx.draw(G, with_labels=True, font_weight='bold', **options)
        st.pyplot(fig)


st.markdown("""<style>
.main {
background-color: #AF9EC;
}</style>""", unsafe_allow_html=True )
