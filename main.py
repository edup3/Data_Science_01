"""
Dashboard de Jugadores - Liga Colombiana de Fútbol
----------------------------------------------------
Simula 1000 registros de jugadores de la Liga BetPlay (Colombia) y presenta
un análisis gráfico interactivo con Streamlit + Plotly.

El dashboard está protegido con una clave de acceso.

Ejecutar con:
    streamlit run main.py
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# Configuración general de la página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Liga Colombiana de Fútbol",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Autenticación por clave de acceso
# ---------------------------------------------------------------------------
CLAVE_ACCESO = "1234"

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔒 Acceso al Dashboard")
    st.caption("Dashboard de jugadores de la Liga Colombiana de Fútbol")

    with st.form("form_login"):
        clave_ingresada = st.text_input("Ingresa la clave de acceso", type="password")
        enviar = st.form_submit_button("Ingresar")

    if enviar:
        if clave_ingresada == CLAVE_ACCESO:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Clave incorrecta. Inténtalo de nuevo.")

    st.stop()

# Botón de cierre de sesión (visible una vez autenticado)
with st.sidebar:
    if st.button("🔓 Cerrar sesión"):
        st.session_state.autenticado = False
        st.rerun()
    st.markdown("---")

# ---------------------------------------------------------------------------
# Simulación de datos (1000 registros, 10 columnas)
# ---------------------------------------------------------------------------
@st.cache_data
def generar_datos(n: int = 1000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    nombres = [
        "Juan", "Carlos", "Andrés", "Santiago", "Camilo", "Jefferson",
        "Yerson", "Sebastián", "Cristian", "Deiver", "Rafael", "Dayro",
        "Marino", "Wilder", "Jhon", "Fabián", "Duván", "Luis", "Miguel",
        "Alexander",
    ]
    apellidos = [
        "Rodríguez", "Martínez", "Gómez", "Hernández", "González", "Díaz",
        "Ramírez", "Torres", "Moreno", "Muñoz", "Valencia", "Mosquera",
        "Cuesta", "Perea", "Arias", "Bonilla", "Cárdenas", "Zapata",
        "Palacios", "Riascos",
    ]

    equipos = [
        "Atlético Nacional", "Millonarios", "América de Cali", "Junior",
        "Deportivo Cali", "Independiente Santa Fe", "Once Caldas",
        "Deportivo Pereira", "Atlético Bucaramanga", "Envigado",
        "La Equidad", "Águilas Doradas", "Deportes Tolima",
        "Alianza Petrolera", "Boyacá Chicó", "Independiente Medellín",
    ]

    posiciones = ["Portero", "Defensa", "Mediocampista", "Delantero"]
    pesos_posicion = [0.10, 0.30, 0.35, 0.25]

    filas = []
    for i in range(1, n + 1):
        equipo = rng.choice(equipos)
        posicion = rng.choice(posiciones, p=pesos_posicion)
        edad = int(np.clip(rng.normal(25, 4.5), 17, 39))
        partidos_jugados = int(np.clip(rng.normal(22, 8), 0, 38))
        minutos_jugados = int(
            np.clip(partidos_jugados * rng.normal(75, 15), 0, 38 * 90)
        )

        # Goles y asistencias según posición
        if posicion == "Delantero":
            goles = int(np.clip(rng.poisson(0.45 * partidos_jugados / 3), 0, 30))
            asistencias = int(np.clip(rng.poisson(0.15 * partidos_jugados / 3), 0, 15))
        elif posicion == "Mediocampista":
            goles = int(np.clip(rng.poisson(0.15 * partidos_jugados / 3), 0, 15))
            asistencias = int(np.clip(rng.poisson(0.25 * partidos_jugados / 3), 0, 18))
        elif posicion == "Defensa":
            goles = int(np.clip(rng.poisson(0.05 * partidos_jugados / 3), 0, 8))
            asistencias = int(np.clip(rng.poisson(0.08 * partidos_jugados / 3), 0, 10))
        else:  # Portero
            goles = 0
            asistencias = int(np.clip(rng.poisson(0.02 * partidos_jugados / 3), 0, 2))

        # Valor de mercado (USD): influenciado por edad, goles, asistencias
        pico_edad = 26
        factor_edad = np.exp(-((edad - pico_edad) ** 2) / (2 * 6 ** 2))
        base_valor = rng.normal(350_000, 150_000)
        valor_mercado = (
            base_valor * (0.6 + 0.4 * factor_edad)
            + goles * 25_000
            + asistencias * 15_000
            + minutos_jugados * 200
        )
        valor_mercado = int(np.clip(valor_mercado, 50_000, 8_000_000))

        tarjetas_amarillas = int(np.clip(rng.poisson(0.12 * partidos_jugados), 0, 15))
        tarjetas_rojas = int(rng.choice([0, 0, 0, 0, 1], p=[0.75, 0.1, 0.08, 0.05, 0.02]))

        filas.append(
            {
                "id_jugador": i,
                "nombre": f"{rng.choice(nombres)} {rng.choice(apellidos)}",
                "equipo": equipo,
                "posicion": posicion,
                "edad": edad,
                "partidos_jugados": partidos_jugados,
                "minutos_jugados": minutos_jugados,
                "goles": goles,
                "asistencias": asistencias,
                "valor_mercado_usd": valor_mercado,
            }
        )

    df = pd.DataFrame(filas)
    return df


df = generar_datos()

# ---------------------------------------------------------------------------
# Sidebar - Filtros
# ---------------------------------------------------------------------------
st.sidebar.title("⚽ Filtros")
st.sidebar.caption("Filtra el conjunto de datos simulado de la Liga Colombiana.")

equipos_sel = st.sidebar.multiselect(
    "Equipo", sorted(df["equipo"].unique()), default=sorted(df["equipo"].unique())
)
posiciones_sel = st.sidebar.multiselect(
    "Posición", sorted(df["posicion"].unique()), default=sorted(df["posicion"].unique())
)
edad_min, edad_max = int(df["edad"].min()), int(df["edad"].max())
rango_edad = st.sidebar.slider(
    "Rango de edad", edad_min, edad_max, (edad_min, edad_max)
)

df_filtrado = df[
    df["equipo"].isin(equipos_sel)
    & df["posicion"].isin(posiciones_sel)
    & df["edad"].between(rango_edad[0], rango_edad[1])
]

st.sidebar.markdown("---")
st.sidebar.caption(f"Registros filtrados: **{len(df_filtrado)}** de {len(df)}")

with st.sidebar.expander("Ver datos crudos"):
    st.dataframe(df_filtrado, use_container_width=True, height=300)

# ---------------------------------------------------------------------------
# Encabezado y KPIs
# ---------------------------------------------------------------------------
st.title("⚽ Dashboard Liga Colombiana de Fútbol")
st.caption(
    "Datos simulados de 1000 jugadores. Usa los filtros de la barra lateral "
    "para explorar el conjunto de datos."
)

if df_filtrado.empty:
    st.warning("No hay datos para los filtros seleccionados. Ajusta los filtros.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total goles", f"{df_filtrado['goles'].sum():,}")
col2.metric("Total asistencias", f"{df_filtrado['asistencias'].sum():,}")
col3.metric("Edad promedio", f"{df_filtrado['edad'].mean():.1f} años")
col4.metric(
    "Valor de mercado promedio", f"${df_filtrado['valor_mercado_usd'].mean():,.0f}"
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Fila 1: Distribución de goles + Boxplot por posición
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.subheader("Distribución de goles")
    fig_hist = px.histogram(
        df_filtrado,
        x="goles",
        nbins=20,
        color="posicion",
        marginal="box",
        opacity=0.8,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_hist.update_layout(
        xaxis_title="Goles", yaxis_title="Cantidad de jugadores",
        legend_title="Posición", bargap=0.05,
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with c2:
    st.subheader("Minutos jugados por posición")
    fig_box = px.box(
        df_filtrado,
        x="posicion",
        y="minutos_jugados",
        color="posicion",
        points="outliers",
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    fig_box.update_layout(
        xaxis_title="Posición", yaxis_title="Minutos jugados", showlegend=False
    )
    st.plotly_chart(fig_box, use_container_width=True)

# ---------------------------------------------------------------------------
# Fila 2: Top goleadores + Valor de mercado por equipo
# ---------------------------------------------------------------------------
c3, c4 = st.columns(2)

with c3:
    st.subheader("Top 10 goleadores")
    top_goleadores = df_filtrado.nlargest(10, "goles")[
        ["nombre", "equipo", "goles"]
    ].sort_values("goles")
    fig_bar = px.bar(
        top_goleadores,
        x="goles",
        y="nombre",
        color="goles",
        orientation="h",
        color_continuous_scale="Reds",
        text="equipo",
    )
    fig_bar.update_layout(
        xaxis_title="Goles", yaxis_title="", coloraxis_showscale=False
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with c4:
    st.subheader("Valor de mercado promedio por equipo")
    valor_equipo = (
        df_filtrado.groupby("equipo", as_index=False)["valor_mercado_usd"]
        .mean()
        .sort_values("valor_mercado_usd", ascending=True)
    )
    fig_valor = px.bar(
        valor_equipo,
        x="valor_mercado_usd",
        y="equipo",
        orientation="h",
        color="valor_mercado_usd",
        color_continuous_scale="Tealgrn",
    )
    fig_valor.update_layout(
        xaxis_title="Valor de mercado promedio (USD)", yaxis_title="",
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_valor, use_container_width=True)

# ---------------------------------------------------------------------------
# Fila 3: Dispersión edad vs valor de mercado + Correlación
# ---------------------------------------------------------------------------
c5, c6 = st.columns(2)

with c5:
    st.subheader("Edad vs. Valor de mercado")
    fig_scatter = px.scatter(
        df_filtrado,
        x="edad",
        y="valor_mercado_usd",
        color="posicion",
        size="goles",
        hover_data=["nombre", "equipo", "asistencias"],
        opacity=0.65,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_scatter.update_layout(
        xaxis_title="Edad", yaxis_title="Valor de mercado (USD)",
        legend_title="Posición",
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with c6:
    st.subheader("Correlación entre variables numéricas")
    num_cols = [
        "edad", "partidos_jugados", "minutos_jugados",
        "goles", "asistencias", "valor_mercado_usd",
    ]
    corr = df_filtrado[num_cols].corr()
    fig_heat = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.columns,
            colorscale="RdBu",
            zmid=0,
            text=corr.round(2).values,
            texttemplate="%{text}",
        )
    )
    fig_heat.update_layout(margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_heat, use_container_width=True)

# ---------------------------------------------------------------------------
# Fila 4: Composición por posición + Sunburst equipo/posición
# ---------------------------------------------------------------------------
c7, c8 = st.columns(2)

with c7:
    st.subheader("Distribución por posición")
    fig_pie = px.pie(
        df_filtrado,
        names="posicion",
        color="posicion",
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_pie.update_traces(textinfo="percent+label")
    st.plotly_chart(fig_pie, use_container_width=True)

with c8:
    st.subheader("Jerarquía: equipo → posición")
    sunburst_df = (
        df_filtrado.groupby(["equipo", "posicion"], as_index=False)[
            "valor_mercado_usd"
        ].mean()
    )
    fig_sun = px.sunburst(
        sunburst_df,
        path=["equipo", "posicion"],
        values=None,
        color="valor_mercado_usd",
        color_continuous_scale="RdYlGn",
    )
    st.plotly_chart(fig_sun, use_container_width=True)

st.markdown("---")
st.caption(
    "Dashboard construido con Streamlit y Plotly · Datos generados de forma "
    "sintética con fines demostrativos · Acceso protegido por clave."
)
