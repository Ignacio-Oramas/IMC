"""
Lógica funcional para el cálculo del IMC y salud.
Estas son funciones puras: misma entrada, misma salida, sin efectos secundarios.
"""

def calcular_imc(peso: float, altura: float) -> float:
    """
    Calcula el Índice de Masa Corporal.
    Fórmula: peso (kg) / [altura (m)]^2
    """
    if altura <= 0:
        raise ValueError("La altura debe ser mayor que cero.")
    if peso <= 0:
        raise ValueError("El peso debe ser mayor que cero.")
        
    return round(peso / (altura ** 2), 2)

def obtener_categoria_imc(imc: float) -> str:
    """
    Devuelve la categoría según el IMC.
    """
    if imc < 18.5:
        return "Bajo peso"
    elif imc < 24.9:
        return "Normal"
    elif imc < 29.9:
        return "Sobrepeso"
    else:
        return "Obesidad"
