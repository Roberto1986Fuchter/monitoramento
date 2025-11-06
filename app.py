import dash
from dash import dcc, html, Input, Output, dash_table
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Configuração do app Dash
app = dash.Dash(__name__)

# Meta tags para mobile
app.index_string = '''
<!DOCTYPE html>
<html lang="pt-br" translate="no">
<head>
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
    {%css%}
    <meta name="google" content="notranslate">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    {%app_entry%}
    <footer>
        {%config%}
        {%scripts%}
        {%renderer%}
    </footer>
</body>
</html>
'''

# Função para buscar TODOS os registros via API (sem filtro)
def get_all_data():
    try:
        url = "https://lightsalmon-goldfinch-301794.hostingersite.com/api_dados.php"
        print(f"Fazendo requisição para: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)

        print(f"Dados recebidos: {len(df)} registros")

        if not df.empty:
            df['data_hora'] = pd.to_datetime(df['data_hora'])
            df = df.sort_values('data_hora')
            print(f"Período dos dados: {df['data_hora'].min()} até {df['data_hora'].max()}")

        return df

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição HTTP: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return pd.DataFrame()

# Função para filtrar dados localmente baseado no time_range
def filter_data_by_time_range(df, time_range):
    if df.empty:
        return df

    latest_date = df['data_hora'].max()

    if time_range == "1h":
        start_date = latest_date - timedelta(hours=1)
    elif time_range == "24h":
        start_date = latest_date - timedelta(hours=24)
    elif time_range == "7d":
        start_date = latest_date - timedelta(days=7)
    elif time_range == "30d":
        start_date = latest_date - timedelta(days=30)
    elif time_range == "365d":
        start_date = latest_date - timedelta(days=365)
    else:
        start_date = latest_date - timedelta(days=30)

    filtered_df = df[df['data_hora'] >= start_date]
    print(f"Filtro aplicado: {time_range} - {len(filtered_df)} registros de {start_date} até {latest_date}")

    return filtered_df


# Layout do Dash
app.layout = html.Div([
    # Cabeçalho
    # Cabeçalho fixo (sticky)
# Cabeçalho responsivo
html.Div([
    html.Img(src="/assets/indubor.jpg", style={
        "height": "35px",
        "marginRight": "10px"
    }),
    html.H1("Temperatura e Umidade (Armazenagem Compostos)", style={
        "textAlign": "center",
        "color": "#FFFFFF",
        "fontFamily": "Arial",
        "margin": "0",
        "flexGrow": "1",
        "fontSize": "18px",  # Reduzido para mobile
        "lineHeight": "1.2"
    }),
    html.Img(src="/assets/4remove.png", style={
        "height": "40px",
        "marginLeft": "10px"
    }),
], style={
    "display": "flex",
    "alignItems": "center",
    "justifyContent": "space-between",
    "width": "100%",
    "padding": "8px 5px",  # Padding reduzido
    "marginBottom": "10px",
    "backgroundColor": "#2C2C2C",
    "position": "sticky",
    "top": "0",
    "zIndex": "1000",
}),


    # Dropdown
    # Dropdown mobile
html.Div([
    dcc.Dropdown(
        id="time-range-dropdown",
        options=[
            {"label": "1 hora", "value": "1h"},
            {"label": "24 horas", "value": "24h"},
            {"label": "7 dias", "value": "7d"},
            {"label": "30 dias", "value": "30d"},
            {"label": "365 dias", "value": "365d"}
        ],
        value="24h",
        clearable=False,
        style={
            "width": "100%",  # Largura total no mobile
            "maxWidth": "300px",
            "fontFamily": "calibri",
            "fontSize": "14px"
        }
    )
], style={"display": "flex", "justifyContent": "center", "marginBottom": "15px", "padding": "0 10px"}),

    # Gráficos
    # Gráficos - Layout Responsivo
html.Div([
    # Temperatura - Mobile Friendly
    html.Div([
        # Gráfico em linha única no mobile
        dcc.Graph(id="graph-temp", style={"height": "250px", "width": "100%"}),
        
        # Indicadores abaixo do gráfico no mobile
        html.Div([
            html.Div([
                html.Div("MÁXIMO", style={"backgroundColor": "#FF4500", "padding": "8px",
                                         "borderRadius": "5px", "color": "white", "textAlign": "center",
                                         "fontSize": "14px", "marginBottom": "4px"}),
                html.Div(id="max-temp", style={"backgroundColor": "#555", "padding": "12px",
                                               "borderRadius": "5px", "color": "white", "textAlign": "center",
                                               "fontSize": "20px", "fontWeight": "bold", "marginBottom": "8px"})
            ], style={"flex": "1", "margin": "5px"}),
            
            html.Div([
                html.Div("MÍNIMO", style={"backgroundColor": "#87CEEB", "padding": "8px",
                                         "borderRadius": "5px", "color": "white", "textAlign": "center",
                                         "fontSize": "14px", "marginBottom": "4px"}),
                html.Div(id="min-temp", style={"backgroundColor": "#555", "padding": "12px",
                                               "borderRadius": "5px", "color": "white", "textAlign": "center",
                                               "fontSize": "20px", "fontWeight": "bold"})
            ], style={"flex": "1", "margin": "5px"})
        ], style={"display": "flex", "justifyContent": "space-between", "width": "100%", "marginTop": "10px"})
    ], style={"marginBottom": "25px", "width": "100%"}),

    # Umidade - Mesma estrutura
    html.Div([
        dcc.Graph(id="graph-umid", style={"height": "250px", "width": "100%"}),
        
        html.Div([
            html.Div([
                html.Div("MÁXIMO", style={"backgroundColor": "#FF4500", "padding": "8px",
                                         "borderRadius": "5px", "color": "white", "textAlign": "center",
                                         "fontSize": "14px", "marginBottom": "4px"}),
                html.Div(id="max-umid", style={"backgroundColor": "#555", "padding": "12px",
                                               "borderRadius": "5px", "color": "white", "textAlign": "center",
                                               "fontSize": "20px", "fontWeight": "bold", "marginBottom": "8px"})
            ], style={"flex": "1", "margin": "5px"}),
            
            html.Div([
                html.Div("MÍNIMO", style={"backgroundColor": "#87CEEB", "padding": "8px",
                                         "borderRadius": "5px", "color": "white", "textAlign": "center",
                                         "fontSize": "14px", "marginBottom": "4px"}),
                html.Div(id="min-umid", style={"backgroundColor": "#555", "padding": "12px",
                                               "borderRadius": "5px", "color": "white", "textAlign": "center",
                                               "fontSize": "20px", "fontWeight": "bold"})
            ], style={"flex": "1", "margin": "5px"})
        ], style={"display": "flex", "justifyContent": "space-between", "width": "100%", "marginTop": "10px"})
    ], style={"marginBottom": "20px", "width": "100%"})
], style={"padding": "10px"}),

    # 🔹 Tabela mais próxima dos gráficos
    # Tabela mobile
html.Div([
    html.H3("Últimos 20 Registros", style={
        "color": "white",
        "textAlign": "center",
        "marginTop": "5px",
        "marginBottom": "8px",
        "fontFamily": "Arial",
        "fontSize": "18px"  # Reduzido
    }),
    dash_table.DataTable(
        id='table-latest-data',
        columns=[
            {"name": "Data/Hora", "id": "data_hora"},
            {"name": "Temp (°C)", "id": "temperatura"},  # Nome mais curto
            {"name": "Umid (%)", "id": "umidade"}        # Nome mais curto
        ],
        style_table={
            "width": "100%",  # Largura total
            "margin": "auto",
            "overflowX": "auto",
            "border": "1px solid #555"
        },
        style_header={
            "backgroundColor": "#333",
            "color": "white",
            "fontWeight": "bold",
            "textAlign": "center",
            "fontSize": "12px",  # Reduzido
            "border": "1px solid #555"
        },
        style_cell={
            "backgroundColor": "#2C2C2C",
            "color": "white",
            "textAlign": "center",
            "padding": "4px",   # Padding reduzido
            "fontFamily": "calibri",
            "fontSize": "11px", # Reduzido
            "border": "1px solid #555",
            "minWidth": "80px"  # Largura mínima
        },
        page_size=20
    )
], style={"padding": "0 10px"}),

    dcc.Interval(id="interval-component", interval=30000, n_intervals=0),
    dcc.Store(id='stored-data')
], style={"backgroundColor": "#2C2C2C", "padding": "15px", "minHeight": "100vh", "margin": "0"})


# Callback para carregar e armazenar os dados
@app.callback(
    Output('stored-data', 'data'),
    Input('interval-component', 'n_intervals')
)
def load_data(n):
    df = get_all_data()
    return df.to_json(date_format='iso', orient='split')


# Callback principal
@app.callback(
    [Output("graph-temp", "figure"),
     Output("graph-umid", "figure"),
     Output("max-temp", "children"),
     Output("min-temp", "children"),
     Output("max-umid", "children"),
     Output("min-umid", "children"),
     Output("table-latest-data", "data")],
    [Input("stored-data", "data"),
     Input("time-range-dropdown", "value")]
)
def update_graphs(stored_data, time_range):
    print(f"Atualizando gráficos com intervalo: {time_range}")

    if stored_data is None:
        df = pd.DataFrame()
    else:
        df = pd.read_json(stored_data, orient='split')
        df['data_hora'] = pd.to_datetime(df['data_hora'])

    filtered_df = filter_data_by_time_range(df, time_range)
    bg_color = "#2C2C2C"

    # --- Temperatura ---
    if not filtered_df.empty:
        fig_temp = px.line(filtered_df, x="data_hora", y="temperatura", title="Temperatura x Tempo")
        max_temp = filtered_df["temperatura"].max()
        min_temp = filtered_df["temperatura"].min()
        max_temp_text = f"{max_temp:.1f}°C"
        min_temp_text = f"{min_temp:.1f}°C"
    else:
        fig_temp = px.line(title="Temperatura x Tempo (Sem dados)")
        max_temp_text = "N/D"
        min_temp_text = "N/D"

    fig_temp.update_layout(
        yaxis=dict(range=[5, 40], showgrid=False),
        xaxis=dict(showgrid=False),
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color="white"),
        height=220,
        margin=dict(l=40, r=40, t=40, b=40)
    )

    if not filtered_df.empty:
        fig_temp.add_hline(
            y=25, line_dash="dash", line_color="red", line_width=2,
            annotation_text="Limite de 25°C", annotation_position="top right",
            annotation_font=dict(color="white", size=11)
        )

    # --- Umidade ---
    if not filtered_df.empty:
        fig_umid = px.line(filtered_df, x="data_hora", y="umidade", title="Umidade x Tempo")
        max_umid = filtered_df["umidade"].max()
        min_umid = filtered_df["umidade"].min()
        max_umid_text = f"{max_umid:.1f}%"
        min_umid_text = f"{min_umid:.1f}%"
    else:
        fig_umid = px.line(title="Umidade x Tempo (Sem dados)")
        max_umid_text = "N/D"
        min_umid_text = "N/D"

    fig_umid.update_layout(
        yaxis=dict(range=[0, 100], showgrid=False),
        xaxis=dict(showgrid=False),
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color="white"),
        height=220,
        margin=dict(l=40, r=40, t=40, b=40)
    )

    if not filtered_df.empty:
        fig_umid.add_hline(
            y=40, line_dash="dash", line_color="#FFA500", line_width=2,
            annotation_text="Seco (40%)", annotation_position="bottom right",
            annotation_font=dict(color="white", size=11)
        )
        fig_umid.add_hline(
            y=90, line_dash="dot", line_color="#87CEEB", line_width=2,
            annotation_text="Úmido (90%)", annotation_position="top right",
            annotation_font=dict(color="white", size=11)
        )

    # 🔹 Últimos 20 registros em ordem decrescente
    if not filtered_df.empty:
        last20 = filtered_df.sort_values('data_hora', ascending=False).head(20)
        last20 = last20[['data_hora', 'temperatura', 'umidade']]
        last20['data_hora'] = last20['data_hora'].dt.strftime("%d/%m/%Y %H:%M:%S")
        table_data = last20.to_dict('records')
    else:
        table_data = []

    return fig_temp, fig_umid, max_temp_text, min_temp_text, max_umid_text, min_umid_text, table_data


server = app.server

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8050, debug=False)


