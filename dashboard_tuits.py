import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import nltk
import re
import networkx as nx
import emoji
import matplotlib.pyplot as plt
nltk.download('punkt')

def quitaEmoUrlPunt(cadena):
    new = emoji.get_emoji_regexp().sub(r'', cadena)
    tokens = new.split()
    palabras = []
    for token in tokens:
        if token.startswith('http'):
            continue
        else:
            palabras.append(token)
    salida = re.sub(r'[^\w\s]', '', " ".join(palabras))
    return salida

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
        total = s.sum()
        s_mod = s.apply(lambda x: round((x*100)/total, 2))
        y = df_can.groupby('PARTIDO_COALICION')['NOMBRE_CANDIDATO'].nunique().sort_values()
        st.header('Porcentaje de participación por partido')
        fig = px.pie(s_mod, values=s_mod.values, names=s_mod.index)
        st.write(fig)
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
        #st.table(df_score_v.assign(hack='').set_index('hack'))
        st.dataframe(df_score_v.assign(hack='').set_index('hack'))
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

        palabras = ['sustentable', 'desarrollo', 'ambiental', 'planeta', 'cambio',
                    'climático', 'contaminación', 'biodiversidad', 'iniciativa', 'conciencia']
        #### CAMBIOS
        st.header('Palabras al rededor')
        options = st.multiselect('Escojer palabras', palabras, ['cambio'])
        cuerpo = " ".join(df_usuarios.Texto_tuit.to_list()).lower()
        new = quitaEmoUrlPunt(cuerpo)
        new = new.split()
        new_cuerpo = []
        for palabra in new:
            if not palabra in stopwords:
                new_cuerpo.append(palabra)
        new_cuerpo = " ".join(new_cuerpo)
        tokens = nltk.word_tokenize(new_cuerpo)
        bgs = nltk.bigrams(tokens)
        fdist = nltk.FreqDist(bgs)
        buscar = []
        if len(options) > 2:
            st.text('Lo máximo que pudes visualizar son dos')
        else:
            for option in options:
                for k,v in fdist.items():
                    if (k[0].startswith(option[:5])) or (k[1].startswith(option[:5])):
                        buscar.append(k)
        G = nx.Graph()
        G.add_edges_from(buscar)

        fig, ax = plt.subplots(figsize=(15, 8))
        pos = nx.spring_layout(G, k=0.4)

        # Plot networks
        nx.draw_networkx(G, pos,
                         font_size=10,
                         width=3,
                         edge_color='grey',
                         node_color='purple',
                         with_labels = False,
                         ax=ax)
        for key, value in pos.items():
            x, y = value[0]+.1, value[1]+.035
            ax.text(x, y,
                    s=key,
                    bbox=dict(facecolor='white', alpha=0.2),
                    horizontalalignment='center', fontsize=11)
        st.pyplot(fig)

st.markdown("""<style>
.main {
background-color: #AF9EC;
}</style>""", unsafe_allow_html=True )
