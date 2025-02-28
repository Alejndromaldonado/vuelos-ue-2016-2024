import pandas as pd
import datetime
import plotly.express as px
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
from datetime import timedelta
import dash_bootstrap_components as dbc
from datetime import timedelta



# importar datos, limpiar y definir variables
# ----------------------------------------------------------------------------
# ID del archivo en Google Drive  
file_id = "1t6wwdI0oh3iWGBVJoWvBVy9Se5JcIylp"  
csv_url = f"https://drive.google.com/uc?id={file_id}"  

# Leer el CSV en bloques de 10,000 filas  
df_chunks = pd.read_csv(csv_url, chunksize=10000)  

# Unir los bloques en un solo DataFrame  
df_raw = pd.concat(df_chunks, ignore_index=True) 
dff_clean = df_raw.copy()

# Limpieza
# # convertir la columna FLT_DATE to datetime
# dff_toclean.loc[:,"FLT_DATE"] = pd.to_datetime(dff_toclean["FLT_DATE"])
# # convertir YEAR y MONTH_NUM a string
# dff_toclean.loc[:,"YEAR"] = dff_toclean["YEAR"].astype(int).astype(str)
# dff_toclean.loc[:,"MONTH_NUM"] = dff_toclean["MONTH_NUM"].astype(int).astype(str)
# # Eliminar las columnas que no necesitamos
# dff_toclean.drop(["FLT_DEP_IFR_2", "FLT_ARR_IFR_2", "FLT_TOT_IFR_2"], axis=1, inplace=True)
# dff_clean = dff_toclean.copy()

# Variables
fecha_max= dff_clean["FLT_DATE"].max()
fecha_min= dff_clean["FLT_DATE"].min()
year_max= dff_clean["YEAR"].max()
year_min= dff_clean["YEAR"].min()
hoy = datetime.date.today()
data_sorce ="https://ansperformance.eu/"
logo_link = "https://upload.wikimedia.org/wikipedia/commons/0/0a/ANS_logo.png"
listado_paises = dff_clean["STATE_NAME"].unique()
listado_years = dff_clean["YEAR"].unique()
listado_aeropuertos = dff_clean["APT_NAME"].unique()
# Promedio Diario vuelos en toda europa
grouped = dff_clean.groupby("FLT_DATE")["FLT_TOT_1"].sum().reset_index()
promedio_dia_sin = round(grouped["FLT_TOT_1"].median())
promedio_dia = f"{promedio_dia_sin:,.0f}".replace(",", ".")
# Promedio de vuelos por aeropuerto en 2016-2024 
airport_traffic = dff_clean.groupby(["APT_NAME"])["FLT_TOT_1"].sum().reset_index()
promedio_vuelos_por_aeropuerto_2016_2024_sin = round(airport_traffic["FLT_TOT_1"].median())
promedio_vuelos_por_aeropuerto_2016_2024 = f"{promedio_vuelos_por_aeropuerto_2016_2024_sin:,.0f}".replace(",", ".")
#numero de aeropuertos en europa
numero_aeropuertos = len(listado_aeropuertos)
date_picker_style = {
    "backgroundColor": "rgb(68, 68, 68)",
    "color": "rgb(170, 170, 170)",
    "border": "1px solid rgb(34, 34, 34)",
    "borderRadius": "5px",
    "padding": "0px",
}
dropdown_style = {
    "backgroundColor": "rgb(50, 56, 62)",
    "color": "rgb(170, 170, 170)",
    "border": "1px solid rgb(50, 56, 62)",
    "borderRadius": "5px",
    "padding": "0px",
}




# Graficos
# ----------------------------------------------------------------------------------------
# ############################################
# ¿Cúanto varia el trafico a lo largo del año?
# Reordenar los meses manualmente
order_months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
# Agrupar por mes para calcular el tráfico total
airport_traffic = dff_clean.groupby("MONTH_MON")["FLT_TOT_1"].sum().reset_index()
# Asegurar que los meses estén ordenados según el orden deseado
airport_traffic["MONTH_MON"] = pd.Categorical(airport_traffic["MONTH_MON"], categories=order_months, ordered=True)
airport_traffic.sort_values("MONTH_MON", inplace=True)
# Grafico de lineas con Plotly Express
fig_linea_tiempo = px.line(airport_traffic, 
                x="MONTH_MON",
                y="FLT_TOT_1", 
                title=f"Cantidad de Vuelos por Mes Acumulados ({year_min}-{year_max})",
                labels={"MONTH_MON": "Mes", "FLT_TOT_1": "Total de Vuelos"})
fig_linea_tiempo.update_layout(paper_bgcolor="rgb(50, 56, 62)",
                  plot_bgcolor="rgb(50, 56, 62)",
                  font=dict(color="rgb(175, 175, 175)"),
                  xaxis=dict(
                      showgrid=False,
                      gridcolor="lightgray",
                      gridwidth=0.5
                  ),
                  yaxis=dict(
                      showgrid=True,
                      gridcolor="lightgray",
                      gridwidth=0.5,
                      griddash="dash"
                  ))

# ###############################################
# ¿Cúales son los paises con mayor trafico aereo?
# Generar un Scatter_mapplot con Plotly Express
# Generar un dataframe con las coordenadas de los paises
# Crear un diccionario con códigos ISO Alpha-3 para los países en el dataset
country_iso_codes = {
    "Albania": "ALB", "Armenia": "ARM", "Austria": "AUT", "Belgium": "BEL",
    "Bosnia and Herzegovina": "BIH", "Bulgaria": "BGR", "Croatia": "HRV", "Cyprus": "CYP",
    "Czech Republic": "CZE", "Denmark": "DNK", "Estonia": "EST", "Finland": "FIN",
    "France": "FRA", "Georgia": "GEO", "Germany": "DEU", "Greece": "GRC",
    "Hungary": "HUN", "Ireland": "IRL", "Italy": "ITA", "Latvia": "LVA",
    "Lithuania": "LTU", "Luxembourg": "LUX", "Malta": "MLT", "Moldova": "MDA",
    "Montenegro": "MNE", "Netherlands": "NLD", "Norway": "NOR", "Poland": "POL",
    "Portugal": "PRT", "Republic of North Macedonia": "MKD", "Romania": "ROU",
    "Serbia": "SRB", "Slovakia": "SVK", "Slovenia": "SVN", "Spain": "ESP",
    "Sweden": "SWE", "Switzerland": "CHE", "Turkey": "TUR", "Ukraine": "UKR",
    "United Kingdom": "GBR", "Israel": "ISR", "Morocco": "MAR", "Iceland": "ISL"
}
# Agregar los códigos ISO al DataFrame
dff_clean.loc[:,"ISO_A3"] = dff_clean["STATE_NAME"].map(country_iso_codes)
# Generar un dataframe con las coordenadas de los paises
df_lat_lon = {
    "ISO_A3": ["ALB", "ARM", "AUT", "BEL", "BIH", "BGR", "HRV", "CYP", "CZE", "DNK", "EST", "FIN", "FRA", "GEO", "DEU", "GRC",
                     "HUN", "IRL", "ITA", "LVA", "LTU", "LUX", "MLT", "MDA", "MNE", "NLD", "NOR", "POL", "PRT", "MKD", "ROU", "SRB",
                     "SVK", "SVN", "ESP", "SWE", "CHE", "TUR", "UKR", "GBR", "ISR", "MAR", "ISL"],
    "latitude": [41.153332, 40.069099, 47.516231, 50.503887, 43.915886, 42.733883, 45.1, 35.126413, 49.817492, 56.26392,
                 58.595272, 61.92411, 46.227638, 42.315407, 51.165691, 39.074208, 47.162494, 53.41291, 41.87194,
                 56.879635, 55.169438, 49.815273, 35.937496, 47.411631, 42.708678, 52.132633, 60.472024, 51.919438,
                 39.399872, 41.9981, 45.943161, 44.016521, 48.669026, 46.151241, 40.463667, 60.128161, 46.818188,
                 38.963745, 48.379433, 55.378051, 31.046051, 31.791702, 64.963051],
    "longitude": [20.168331, 45.038189, 14.550072, 4.469936, 17.679076, 25.48583, 15.2, 33.429859, 15.472962, 9.501785,
                  25.013607, 25.748151, 2.213749, 43.356892, 10.451526, 21.824312, 19.503304, -8.24389, 12.56738,
                  24.603189, 23.881275, 6.129583, 14.375416, 28.369885, 19.37439, 5.291266, 8.468946, 19.145136,
                  -8.224454, 21.4254, 24.96676, 21.005859, 19.699024, 14.995463, -3.74922, 18.643501, 8.227512,
                  35.243322, 31.16558, -3.435973, 34.851612, -7.09262, -19.020835]
}
# convertir el diccionario a un dataframe
df = pd.DataFrame(df_lat_lon)
# Agregar las coordenadas al DataFrame de vuelos
dff_map_clean = dff_clean.merge(df, on="ISO_A3", how="left")
data_map = dff_map_clean[["YEAR","MONTH_MON","MONTH_NUM","FLT_DATE","ISO_A3","STATE_NAME", "FLT_TOT_1", "latitude", "longitude"]]
# agrupar por ISO_A3 y contar los vuelos
data_map_grouped = data_map.groupby(["ISO_A3", "STATE_NAME", "latitude", "longitude"])["FLT_TOT_1"].sum().reset_index()
# Crear el Scatter Map Plot
fig_scatter_map = px.scatter_map(data_map_grouped, 
                                    lat="latitude", 
                                    lon="longitude", 
                                    color="FLT_TOT_1", 
                                    size="FLT_TOT_1",
                                    hover_name="STATE_NAME", 
                                    title=f"Total de Vuelos por País ({year_min}-{year_max})",
                                    color_continuous_scale="ylgn",
                                    size_max=25,
                                    zoom=2,
                                    labels={"FLT_TOT_1": "Total de Vuelos"},
                                    center={"lat": 50, "lon": 10},
                                    map_style="carto-darkmatter")
fig_scatter_map.update_layout(paper_bgcolor="rgb(50, 56, 62)",
                  plot_bgcolor="rgb(50, 56, 62)",
                  font=dict(color="rgb(175, 175, 175)"),
                  margin=dict(l=20, r=20, t=50, b=20)
                  )

# #####################################################################
# ¿Cúales son los aeropuertos con mas trafico en Europa?
# Agrupar por año y aeropuerto para calcular el tráfico total
airport_traffic = dff_clean.groupby(["YEAR", "APT_NAME"])["FLT_TOT_1"].sum().reset_index()
# calcular el top 10 de los aeropuertos con mayor trafico total del 2016 al 2024
top_airports = airport_traffic.groupby("APT_NAME")["FLT_TOT_1"].sum().nlargest(10).reset_index(name="FLT_TOT_1")
# Grafico de barras horizontales con Plotly Express
fig_bar_top10_aerop = px.bar(top_airports, 
                     y="APT_NAME", 
                     x="FLT_TOT_1", 
                     #color="YEAR", 
                     orientation="h", 
                     title=f"Top 10 Aeropuertos con Mayor Tráfico Acumulado del {year_min} al {year_max}",
                     labels={"APT_NAME": "Aeropuerto", "FLT_TOT_1": "Total de Vuelos"})

fig_bar_top10_aerop.update_layout(paper_bgcolor="rgb(50, 56, 62)",
                  plot_bgcolor="rgb(50, 56, 62)",
                  font=dict(color="rgb(175, 175, 175)"),
                  yaxis=dict(
                      showgrid=False,
                      gridcolor="lightgray",
                      gridwidth=0.5
                  ),
                  xaxis=dict(
                      showgrid=True,
                      gridcolor="lightgray",
                      gridwidth=0.5,
                      griddash="dash"
                  ))

# ###########################################
# ¿Existe un patron semanal de trafico aereo?
week_pattern= dff_clean.copy()
week_pattern["DAY_OF_WEEK"] = pd.to_datetime(week_pattern["FLT_DATE"]).dt.day_name()
week_pattern_group = week_pattern.groupby("DAY_OF_WEEK")["FLT_TOT_1"].sum().reset_index()
# Crear grafico de linea por dia de la semana
fig_week_pattern = px.bar(week_pattern_group,
                    x="DAY_OF_WEEK",
                    y="FLT_TOT_1",
                    color_continuous_scale="inferno",
                    title="Total de Vuelos por Dia de la Semana",
                    category_orders={"DAY_OF_WEEK": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]},
                    labels={"DAY_OF_WEEK": "Día de Semana", "FLT_TOT_1": "Total de Vuelos"})
fig_week_pattern.update_layout(paper_bgcolor="rgb(50, 56, 62)",
                  plot_bgcolor="rgb(50, 56, 62)",
                  font=dict(color="rgb(175, 175, 175)"),
                  xaxis=dict(
                      showgrid=False,
                      gridcolor="lightgray",
                      gridwidth=0.5
                  ),
                  yaxis=dict(
                      showgrid=True,
                      gridcolor="lightgray",
                      gridwidth=0.5,
                      griddash="dash"
                  ))



# Definir la App y su diseño
# ----------------------------------------------------------------------------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])
#server = app.server

# Layout del dashboard
app.layout = dbc.Container([
    # Encabezado
    dbc.Row([
        dbc.Col(html.Img(src="https://i.postimg.cc/5NNHf0Qq/flag-of-europe-european-union-eu-flag-in-design-shape-vector-removebg-preview.png", height="75px"), width="auto"),
        dbc.Col(html.H1(f"Europa en el Aire: Análisis del Trafico Aereo {year_min}-{year_max}", className="text-center", style={"color": "rgb(240, 255, 255)","font-size": "65px", "margin": "10px 0px 0px 40px"}), width=10),
        dbc.Col(children=[
            html.Span(children=[html.H6("Elaborado por: "),
                                html.B("Alejandro Maldonado "),html.Br(),
                                html.I("Analista de Datos")]),
            html.H6("Fuente: "),
            html.A(f"{data_sorce}", href=data_sorce, target="_blank", style={"color": "grey", "text-decoration": "underline", "font-size": "10px"})])
    ], className="mb-4 mt-2 align-items-center"),
        
    # Tarjetas KPI
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("Media de Vuelos Diarios", className="card-title", id="legenda_vuelos_dia", style={"color":"rgb(170, 170, 170)"}),
                html.H2(f"{promedio_dia}", className="card-text", id="vuelos_diarios", style={"font-size":"40px", "color":"rgb(240, 255, 255)"})
            ])
        ], className="text-center shadow"), width=6),
                
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("Numero Total de Aeropuertos", className="card-title", id="pais", style={"color":"rgb(170, 170, 170)"}),
                html.H2(f"{numero_aeropuertos}", className="card-text",id="total_aeropuertos", style={"font-size":"40px", "color":"rgb(240, 255, 255)"})
            ])
        ], className="text-center shadow"), width=6),
    ], className="mb-4"),
    
    # Fila de filtros
    dbc.Row([dbc.Col(dcc.Dropdown(
            id="year_dd",
            options=[{"label": year, "value": year} for year in listado_years],
            placeholder="Selecciona un año",
            className="dropdown",
            style=date_picker_style
        ), width=6),
             dbc.Tooltip("Elige el año del que quieres ver información mensual.",
                         target="year_dd", placement="top"),
        dbc.Col(dcc.DatePickerRange(
            id="date-picker",
            display_format='YYYY-MM-DD',
            start_date_placeholder_text="Fecha inicio",
            end_date_placeholder_text="Fecha fin",
            initial_visible_month="2024-12-31",
            #start_date=fecha_min,
            #end_date=fecha_max,
            className="date-picker-range",
            style=date_picker_style
        ), width=6),
             dbc.Tooltip(f"Elige un rango de fechas entre {year_min} y {year_max} para contar el numero de vuelos por país.",
                         target="date-picker", placement="right"),
    ], className="mb-4"),
    
    # Gráficos
    dbc.Row([
        dbc.Col(dcc.Graph(id="line_chart", figure=fig_linea_tiempo, className="grafico-style", style={"border-radius": "10px", "overflow": "hidden"}), width=6),  # Gráfico de línea de tiempo
        dbc.Col(dcc.Graph(id="map_chart", figure=fig_scatter_map, className="grafico-style", style={"border-radius": "10px", "overflow": "hidden"}), width=6)    # Gráfico de mapa
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id="bar_chart_1", figure=fig_bar_top10_aerop, className="grafico-style", style={"border-radius": "10px", "overflow": "hidden"}), width=6),  # Primer gráfico de barras
        dbc.Col(dcc.Graph(id="bar_chart_2", figure=fig_week_pattern, className="grafico-style", style={"border-radius": "10px", "overflow": "hidden"}), width=6)   # Segundo gráfico de barras
    ], className="mb-4"),

], fluid=True)


# Definir los callbasck y sus funciones
# ---------------------------------------------------------------------------------------

#####################################################
# Modificar el grafico de lineas con un dropdaown
@app.callback([
    Output(component_id="legenda_vuelos_dia",component_property="children"),
    Output(component_id="vuelos_diarios",component_property="children"),
    Output(component_id="line_chart",component_property="figure")],
    Input(component_id="year_dd",component_property="value")
)
def update_line_plot(selection):
    df_to_filter = dff_clean.copy()
    
    if not selection:
        return "Media de Vuelos Diarios",promedio_dia, fig_linea_tiempo
    else:
                
        dff_clean_filtered = df_to_filter[df_to_filter["YEAR"] == selection]
        
        order_months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
        # Agrupar por mes para calcular el tráfico total
        airport_traffic_filtered = dff_clean_filtered.groupby("MONTH_MON")["FLT_TOT_1"].sum().reset_index()
        # Asegurar que los meses estén ordenados según el orden deseado
        airport_traffic_filtered["MONTH_MON"] = pd.Categorical(airport_traffic_filtered["MONTH_MON"], categories=order_months, ordered=True)
        airport_traffic_filtered = airport_traffic_filtered.sort_values("MONTH_MON")
        # Grafico de lineas con Plotly Express
        fig_linea_tiempo_edited = px.line(airport_traffic_filtered, 
                        x="MONTH_MON",
                        y="FLT_TOT_1", 
                        title=f"Cantidad de Vuelos por Mes: {selection}",
                        labels={"MONTH_MON": "Mes", "FLT_TOT_1": "Total de Vuelos"})
        fig_linea_tiempo_edited.update_layout(paper_bgcolor="rgb(50, 56, 62)",
                        plot_bgcolor="rgb(50, 56, 62)",
                        font=dict(color="rgb(175, 175, 175)"),
                        xaxis=dict(
                            showgrid=False,
                        ),
                        yaxis=dict(
                            showgrid=True,
                            gridcolor="lightgray",
                            gridwidth=0.5,
                            griddash="dash"
                        ))
        # Promedio Diario vuelos en toda europa
        grouped_updated = dff_clean_filtered.groupby("FLT_DATE")["FLT_TOT_1"].sum().reset_index()
        promedio_dia_sin_updated = round(grouped_updated["FLT_TOT_1"].median())
        promedio_dia_updated = f"{promedio_dia_sin_updated:,.0f}".replace(",", ".")
        
        
        return  f"Media de Vuelos Diarios: {selection}",f"{promedio_dia_updated}", fig_linea_tiempo_edited
        


################################################################
# Modificar el mapa por el date-picker
@app.callback(
    Output(component_id="map_chart",component_property="figure"),
    Input(component_id="date-picker",component_property="start_date"),
    Input(component_id="date-picker",component_property="end_date")
)
def update_map_plot(start_date, end_date):
    df_map_to_filter = data_map.copy()
    df_map_to_filter["FLT_DATE"] = pd.to_datetime(df_map_to_filter["FLT_DATE"], errors="coerce")
    
    if not start_date or not end_date:
        return fig_scatter_map
    else:
        
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date) + timedelta(days=1)
        
        dff_clean_map_filtered = df_map_to_filter[(df_map_to_filter["FLT_DATE"] >= start_date) & (df_map_to_filter["FLT_DATE"] <= end_date)]
        # agrupar por ISO_A3 y contar los vuelos
        data_map_grouped_updated = dff_clean_map_filtered.groupby(["ISO_A3", "STATE_NAME", "latitude", "longitude"])["FLT_TOT_1"].sum().reset_index()
        # Crear el Scatter Map Plot
        start_date_new = start_date.date()
        end_date_new = end_date.date()
        fig_scatter_map_updated = px.scatter_map(data_map_grouped_updated, 
                                            lat="latitude", 
                                            lon="longitude", 
                                            color="FLT_TOT_1", 
                                            size="FLT_TOT_1",
                                            hover_name="STATE_NAME", 
                                            title=f"Suma de vuelos por país entre {start_date_new} y {end_date_new}",
                                            color_continuous_scale="ylgn",
                                            size_max=25,
                                            zoom=2,
                                            labels={"FLT_TOT_1": "Total de Vuelos"},
                                            center={"lat": 50, "lon": 10},
                                            map_style="carto-darkmatter")
        fig_scatter_map_updated.update_layout(paper_bgcolor="rgb(50, 56, 62)",
                        plot_bgcolor="rgb(50, 56, 62)",
                        font=dict(color="rgb(175, 175, 175)"),
                        margin=dict(l=20, r=20, t=50, b=20)
                        )
        return fig_scatter_map_updated

################################################################
# Modificar la targeta de numero total de Aeropuertos con el Hover sobre el pais en el Mapa
@app.callback([
    Output(component_id="pais",component_property="children"),
    Output(component_id="total_aeropuertos",component_property="children"),
    Output(component_id="bar_chart_2",component_property="figure")],
    Input(component_id="map_chart",component_property="hoverData")
)

def capture_hover_data(hoverData):
    if hoverData is None:
        return "Numero Total de Aeropuertos", f"{numero_aeropuertos}", fig_week_pattern
    pais_seleccionado = hoverData["points"][0]["hovertext"]
    df_hover_pais = dff_clean.copy()
    df_filtrado= df_hover_pais[df_hover_pais["STATE_NAME"]== pais_seleccionado]
    listado_aeropuertos_updated = df_filtrado["APT_NAME"].unique()
    numero_aeropuertos_updated = len(listado_aeropuertos_updated)
    
    # filtrado de tendencia por dia de semana
    df_filtrado["DAY_OF_WEEK"] = pd.to_datetime(df_filtrado["FLT_DATE"]).dt.day_name()
    week_pattern_group_updated = df_filtrado.groupby("DAY_OF_WEEK")["FLT_TOT_1"].sum().reset_index()
    # Crear grafico de linea por dia de la semana
    fig_week_pattern_updated = px.bar(week_pattern_group_updated,
                        x="DAY_OF_WEEK",
                        y="FLT_TOT_1",
                        color_continuous_scale="inferno",
                        title=f"Cantidad de Vuelos por Dia de la Semana: {pais_seleccionado}",
                        category_orders={"DAY_OF_WEEK": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]},
                        labels={"DAY_OF_WEEK": "Día de Semana", "FLT_TOT_1": "Total de Vuelos"})
    fig_week_pattern_updated.update_layout(paper_bgcolor="rgb(50, 56, 62)",
                    plot_bgcolor="rgb(50, 56, 62)",
                    font=dict(color="rgb(175, 175, 175)"),
                    xaxis=dict(
                        showgrid=False,
                        gridcolor="lightgray",
                        gridwidth=0.5
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor="lightgray",
                        gridwidth=0.5,
                        griddash="dash"
                    ))
    
    return f"Numero Total de Aeropuertos: {pais_seleccionado}", f"{numero_aeropuertos_updated}", fig_week_pattern_updated




# Ejecutar la aplicación
# ----------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run_server(debug=True, port=8888)# ,host="0.0.0.0", port=8080, debug=False)
   

