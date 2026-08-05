import plotly.graph_objects as go
import json
import plotly.utils

def generar_json_evolucion_imc(altura: float, pesos_historial: dict) -> str:
    """
    Toma la altura y un diccionario de pesos { 'YYYY-MM': peso }
    y devuelve el JSON para Plotly.
    Función pura de transformación de datos.
    """
    if not pesos_historial:
        return None

    fig = go.Figure()
    
    # Calcular IMC para cada mes y año
    imcs = {fecha: (peso / (altura ** 2)) for fecha, peso in pesos_historial.items()}
    
    # Ordenar los datos por fecha
    fechas = sorted(imcs.keys())
    valores_imc = [imcs[fecha] for fecha in fechas]
    
    fig.add_trace(go.Scatter(
        x=fechas,
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
        xaxis_title="Fecha",
        yaxis_title="IMC",
        hovermode="x unified"
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
