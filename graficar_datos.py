import plotly.graph_objects as go
import json
import plotly.utils
from flask import session
meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

def get_graph_json():
    fig = go.Figure()
    
    # Obtener los datos de IMC de la sesión
    imcs = session.get('imcs', [])
    
    # Ajustar la lista de meses según la cantidad de mediciones
    meses_datos = meses[:len(imcs)]
    
    # Agregar la línea de IMC del usuario
    fig.add_trace(go.Scatter(
        x=meses_datos, 
        y=imcs, 
        mode='lines+markers', 
        name='Tu IMC', 
        connectgaps=False
    ))

    # Configurar el diseño del gráfico
    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Meses",
        yaxis_title="IMC",
        title="Tu Progreso de IMC",
        font=dict(color="white"),
        showlegend=True,
        hovermode='x unified'
    )

    # Agregar líneas de referencia para las categorías de IMC
    fig.add_hline(y=18.5, line_dash="dash", line_color="yellow", annotation_text="IMC Bajo: 18.5")
    fig.add_hline(y=24.9, line_dash="dash", line_color="green", annotation_text="IMC Normal: 24.9")
    fig.add_hline(y=30, line_dash="dash", line_color="orange", annotation_text="IMC Alto (Obesidad): 30")

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)