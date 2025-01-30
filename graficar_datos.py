import plotly.graph_objects as go
import json
import plotly.utils

meses_orden = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
              "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

def json_grafica(altura, pesos):
    fig = go.Figure()
    
    # Calcular IMC para cada mes
    imcs = {mes: (peso / (altura ** 2)) for mes, peso in pesos.items()}
    
    # Ordenar los datos por meses
    meses = [mes for mes in meses_orden if mes in imcs]
    valores_imc = [imcs[mes] for mes in meses]
    
    fig.add_trace(go.Scatter(
        x=meses,
        y=valores_imc,
        mode='lines+markers',
        name='IMC',
        line=dict(color='#00FF00')
    ))
    
    # Líneas de referencia
    lineas_referencia = [
        (18.5, 'IMC Bajo', '#FFA500'),
        (24.9, 'IMC Normal', '#00FF00'),
        (29.9, 'Sobrepeso', '#FF0000')
    ]
    
    for valor, nombre, color in lineas_referencia:
        fig.add_hline(y=valor, line_dash="dash",
                     line_color=color,
                     annotation_text=nombre)
    
    fig.update_layout(
        template="plotly_dark",
        title="Evolución del IMC",
        xaxis_title="Meses",
        yaxis_title="IMC",
        hovermode="x unified"
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)