"""
Dashboard de Calificaciones Escolares
--------------------------------------
Simula 1000 registros de calificaciones de un colegio y presenta un
análisis gráfico interactivo utilizando Streamlit + Plotly.

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
    page_title="Dashboard de Calificaciones Escolares",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Simulación de datos (1000 registros, 10 columnas)
# ---------------------------------------------------------------------------
@st.cache_data
def generar_datos(n: int = 1000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    nombres = [
        "Mateo", "Sofía", "Samuel", "Isabella", "Juan José", "Valentina",
        "Santiago", "Mariana", "Emiliano", "Luciana", "Tomás", "Camila",
        "Nicolás", "Salomé", "Andrés", "Gabriela", "Sebastián", "Antonella",
        "David", "Renata",
    ]
    apellidos = [
        "Gómez", "Rodríguez", "Martínez", "López", "García", "Pérez",
        "Sánchez", "Ramírez", "Torres", "Flórez", "Vargas", "Castro",
        "Ortiz", "Rojas", "Moreno", "Suárez",
    ]

    grados = ["6°", "7°", "8°", "9°", "10°", "11°"]
    secciones = ["A", "B", "C"]
    materias = [
        "Matemáticas", "Ciencias Naturales", "Lengua Castellana",
        "Ciencias Sociales", "Inglés", "Educación Física", "Artística",
        "Tecnología",
    ]
    generos = ["Masculino", "Femenino"]
    periodos = ["Periodo 1", "Periodo 2", "Periodo 3", "Periodo 4"]

    # Sesgos leves por materia y periodo para que el análisis sea interesante
    sesgo_materia = {
        "Matemáticas": -0.25, "Ciencias Naturales": -0.1,
        "Lengua Castellana": 0.05, "Ciencias Sociales": 0.1,
        "Inglés": -0.05, "Educación Física": 0.35,
        "Artística": 0.3, "Tecnología": 0.15,
    }
    sesgo_periodo = {
        "Periodo 1": -0.1, "Periodo 2": 0.0,
        "Periodo 3": 0.05, "Periodo 4": 0.15,
    }

    filas = []
    for i in range(1, n + 1):
        grado = rng.choice(grados)
        seccion = rng.choice(secciones)
        materia = rng.choice(materias)
        periodo = rng.choice(periodos)
        genero = rng.choice(generos)
        horas_estudio = float(np.clip(rng.normal(6, 2.5), 0, 20))

        base = rng.normal(3.7, 0.6)
        efecto_estudio = (horas_estudio - 6) * 0.03
        calificacion = (
            base
            + sesgo_materia[materia]
            + sesgo_periodo[periodo]
            + efecto_estudio
        )
        calificacion = float(np.clip(calificacion, 0.5, 5.0))

        asistencia = float(np.clip(rng.normal(90, 8), 40, 100))

        filas.append(
            {
                "id_estudiante": i,
                "nombre": f"{rng.choice(nombres)} {rng.choice(apellidos)}",
                "grado": grado,
                "seccion": seccion,
                "materia": materia,
                "periodo": periodo,
                "genero": genero,
                "calificacion": round(calificacion, 1),
                "asistencia_%": round(asistencia, 1),
                "horas_estudio_semanal": round(horas_estudio, 1),
            }
        )

    df = pd.DataFrame(filas)
    return df


df = generar_datos()

# ---------------------------------------------------------------------------
# Sidebar - Filtros
# ---------------------------------------------------------------------------
st.sidebar.title("🎓 Filtros")
st.sidebar.caption("Filtra el conjunto de datos simulado del colegio.")

grados_sel = st.sidebar.multiselect(
    "Grado", sorted(df["grado"].unique()), default=sorted(df["grado"].unique())
)
materias_sel = st.sidebar.multiselect(
    "Materia", sorted(df["materia"].unique()), default=sorted(df["materia"].unique())
)
periodos_sel = st.sidebar.multiselect(
    "Periodo", sorted(df["periodo"].unique()), default=sorted(df["periodo"].unique())
)
genero_sel = st.sidebar.multiselect(
    "Género", sorted(df["genero"].unique()), default=sorted(df["genero"].unique())
)

df_filtrado = df[
    df["grado"].isin(grados_sel)
    & df["materia"].isin(materias_sel)
    & df["periodo"].isin(periodos_sel)
    & df["genero"].isin(genero_sel)
]

st.sidebar.markdown("---")
st.sidebar.caption(f"Registros filtrados: **{len(df_filtrado)}** de {len(df)}")

with st.sidebar.expander("Ver datos crudos"):
    st.dataframe(df_filtrado, use_container_width=True, height=300)

# ---------------------------------------------------------------------------
# Encabezado y KPIs
# ---------------------------------------------------------------------------
st.title("🎓 Dashboard de Calificaciones Escolares")
st.caption(
    "Datos simulados de 1000 registros académicos. Usa los filtros de la "
    "barra lateral para explorar el conjunto de datos."
)

if df_filtrado.empty:
    st.warning("No hay datos para los filtros seleccionados. Ajusta los filtros.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Promedio general", f"{df_filtrado['calificacion'].mean():.2f}")
col2.metric("Asistencia promedio", f"{df_filtrado['asistencia_%'].mean():.1f}%")
col3.metric(
    "Horas de estudio prom.", f"{df_filtrado['horas_estudio_semanal'].mean():.1f} h"
)
col4.metric(
    "% Aprobación (≥3.0)",
    f"{(df_filtrado['calificacion'] >= 3.0).mean() * 100:.1f}%",
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Fila 1: Distribución de calificaciones + Boxplot por materia
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.subheader("Distribución de calificaciones")
    fig_hist = px.histogram(
        df_filtrado,
        x="calificacion",
        nbins=25,
        color="genero",
        marginal="box",
        opacity=0.8,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_hist.update_layout(
        xaxis_title="Calificación", yaxis_title="Cantidad de estudiantes",
        legend_title="Género", bargap=0.05,
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with c2:
    st.subheader("Calificaciones por materia")
    fig_box = px.box(
        df_filtrado,
        x="materia",
        y="calificacion",
        color="materia",
        points="outliers",
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    fig_box.update_layout(
        xaxis_title="Materia", yaxis_title="Calificación", showlegend=False
    )
    fig_box.update_xaxes(tickangle=-30)
    st.plotly_chart(fig_box, use_container_width=True)

# ---------------------------------------------------------------------------
# Fila 2: Promedio por grado + Evolución por periodo
# ---------------------------------------------------------------------------
c3, c4 = st.columns(2)

with c3:
    st.subheader("Promedio de calificación por grado")
    prom_grado = (
        df_filtrado.groupby("grado", as_index=False)["calificacion"]
        .mean()
        .sort_values("grado")
    )
    fig_bar = px.bar(
        prom_grado,
        x="grado",
        y="calificacion",
        color="calificacion",
        color_continuous_scale="Tealgrn",
        text_auto=".2f",
    )
    fig_bar.update_layout(
        xaxis_title="Grado", yaxis_title="Calificación promedio",
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with c4:
    st.subheader("Evolución del promedio por periodo")
    prom_periodo = (
        df_filtrado.groupby(["periodo", "materia"], as_index=False)["calificacion"]
        .mean()
    )
    fig_line = px.line(
        prom_periodo,
        x="periodo",
        y="calificacion",
        color="materia",
        markers=True,
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    fig_line.update_layout(
        xaxis_title="Periodo", yaxis_title="Calificación promedio",
        legend_title="Materia",
    )
    st.plotly_chart(fig_line, use_container_width=True)

# ---------------------------------------------------------------------------
# Fila 3: Dispersión horas de estudio vs calificación + Correlación
# ---------------------------------------------------------------------------
c5, c6 = st.columns(2)

with c5:
    st.subheader("Horas de estudio vs. Calificación")
    fig_scatter = px.scatter(
        df_filtrado,
        x="horas_estudio_semanal",
        y="calificacion",
        color="genero",
        size="asistencia_%",
        hover_data=["nombre", "grado", "materia"],
        trendline="ols",
        opacity=0.6,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_scatter.update_layout(
        xaxis_title="Horas de estudio semanales", yaxis_title="Calificación",
        legend_title="Género",
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with c6:
    st.subheader("Correlación entre variables numéricas")
    num_cols = ["calificacion", "asistencia_%", "horas_estudio_semanal"]
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
# Fila 4: Composición por género + Sunburst grado/sección/materia
# ---------------------------------------------------------------------------
c7, c8 = st.columns(2)

with c7:
    st.subheader("Distribución por género")
    fig_pie = px.pie(
        df_filtrado,
        names="genero",
        color="genero",
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_pie.update_traces(textinfo="percent+label")
    st.plotly_chart(fig_pie, use_container_width=True)

with c8:
    st.subheader("Jerarquía: grado → sección → materia")
    sunburst_df = (
        df_filtrado.groupby(["grado", "seccion", "materia"], as_index=False)[
            "calificacion"
        ].mean()
    )
    fig_sun = px.sunburst(
        sunburst_df,
        path=["grado", "seccion", "materia"],
        values=None,
        color="calificacion",
        color_continuous_scale="RdYlGn",
        range_color=[0, 5],
    )
    st.plotly_chart(fig_sun, use_container_width=True)

st.markdown("---")
st.caption(
    "Dashboard construido con Streamlit y Plotly · Datos generados de forma "
    "sintética con fines demostrativos."
)
