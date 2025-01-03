import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import io

st.set_page_config(layout="wide")

def obtener_datos_paises():
    """Obtiene los datos de países desde la API REST."""
    url = 'https://raw.githubusercontent.com/jxnscv/Programacion/main/all.json'
    try:
        respuesta = requests.get(url, timeout=10)
        respuesta.raise_for_status()
        return respuesta.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al conectarse a la API: {e}")
        return []

def convertir_a_dataframe(paises):
    """Convierte la lista de países en un DataFrame."""
    datos = []
    for pais in paises:
        datos.append({
            'Nombre Común': pais.get('name', {}).get('common', None),
            'Región Geográfica': pais.get('region', None),
            'Población Total': pais.get('population', 0),
            'Área en km²': pais.get('area', 0),
            'Número de Fronteras': len(pais.get('borders', [])),
            'Número de Idiomas Oficiales': len(pais.get('languages', {})),
            'Número de Zonas Horarias': len(pais.get('timezones', []))
        })
    return pd.DataFrame(datos)

paises = obtener_datos_paises()
df = convertir_a_dataframe(paises)

st.title('Análisis de Datos de Países 🌍')

st.sidebar.title("Navegación")
pagina = st.sidebar.radio("Selecciona una página", ["Descripción", "Interacción con Datos", "Gráficos Interactivos"])

if pagina == "Descripción":
    st.markdown("### **Descripción del Proyecto**")
    st.write("""
    Esta aplicación web utiliza datos de la API [REST Countries](https://restcountries.com/v3.1/all).
    Permite explorar información sobre países, incluyendo población, área, idiomas, fronteras y más.
    La aplicación está dividida en tres secciones:
    - **Descripción**: Información sobre el proyecto y la fuente de datos.
    - **Interacción con Datos**: Visualiza, filtra y exporta datos.
    - **Gráficos Interactivos**: Genera gráficos dinámicos basados en los datos.
    """)

elif pagina == "Interacción con Datos":
    st.markdown("### **Interacción con Datos**")

    st.subheader("Datos Originales")
    if st.checkbox('Mostrar datos originales'):
        st.dataframe(df)

    st.subheader("Estadísticas")
    columna_estadisticas = st.selectbox("Selecciona una columna numérica para calcular estadísticas", ["Población Total", "Área en km²"])
    if columna_estadisticas:
        st.markdown(f"""
        - **Media:** {df[columna_estadisticas].mean():,.2f}  
        - **Mediana:** {df[columna_estadisticas].median():,.2f}  
        - **Desviación Estándar:** {df[columna_estadisticas].std():,.2f}
        """)

    st.subheader("Ordenar Datos")
    columna_ordenar = st.selectbox("Selecciona una columna para ordenar", df.columns)
    orden = st.radio("Orden", ["Ascendente", "Descendente"])
    if columna_ordenar:
        df_ordenado = df.sort_values(by=columna_ordenar, ascending=(orden == "Ascendente"))
        st.dataframe(df_ordenado)

    st.subheader("Filtrar por Población")
    rango_min, rango_max = st.slider("Selecciona un rango de población", int(df["Población Total"].min()), int(df["Población Total"].max()), (0, int(df["Población Total"].max())))
    df_filtrado = df[(df["Población Total"] >= rango_min) & (df["Población Total"] <= rango_max)]
    st.dataframe(df_filtrado)

    if st.button('Descargar datos filtrados'):
        csv = df_filtrado.to_csv(index=False)
        st.download_button('Descargar CSV', csv, 'datos_filtrados.csv', 'text/csv')

elif pagina == "Gráficos Interactivos":
    st.markdown("### **Gráficos Interactivos**")
    
    st.subheader("Configurar Gráfico")
    x_var = st.selectbox("Eje X", ["Población Total", "Área en km²", "Número de Fronteras", "Número de Idiomas Oficiales", "Número de Zonas Horarias"])
    y_var = st.selectbox("Eje Y", ["Población Total", "Área en km²", "Número de Fronteras", "Número de Idiomas Oficiales", "Número de Zonas Horarias"])
    tipo_grafico = st.selectbox("Tipo de Gráfico", ["Dispersión", "Línea", "Barras"])

    # Configuración de rango personalizado
    st.subheader("Rango Personalizado para Ejes")
    rango_x_min, rango_x_max = st.slider(
        f"Selecciona el rango para el eje X ({x_var})",
        float(df[x_var].min()), float(df[x_var].max()),
        (float(df[x_var].min()), float(df[x_var].max()))
    )
    rango_y_min, rango_y_max = st.slider(
        f"Selecciona el rango para el eje Y ({y_var})",
        float(df[y_var].min()), float(df[y_var].max()),
        (float(df[y_var].min()), float(df[y_var].max()))
    )

    fig, ax = plt.subplots()
    if tipo_grafico == "Dispersión":
        ax.scatter(df[x_var], df[y_var], alpha=0.7)
    elif tipo_grafico == "Línea":
        ax.plot(df[x_var], df[y_var], marker='o')
    elif tipo_grafico == "Barras":
        ax.bar(df[x_var], df[y_var])


    ax.set_xlim(rango_x_min, rango_x_max)
    ax.set_ylim(rango_y_min, rango_y_max)
    ax.set_xlabel(x_var)
    ax.set_ylabel(y_var)
    ax.set_title(f"{tipo_grafico} entre {x_var} y {y_var}")
    st.pyplot(fig)

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)
    st.download_button("Descargar Gráfico", buffer, file_name="grafico.png")

