import pytest
from src.core.imc import calcular_imc, obtener_categoria_imc

def test_calcular_imc_normal():
    # Peso 70kg, Altura 1.75m -> IMC ~ 22.86
    assert calcular_imc(70, 1.75) == 22.86

def test_calcular_imc_obesidad():
    # Peso 100kg, Altura 1.70m -> IMC ~ 34.60
    assert calcular_imc(100, 1.70) == 34.60

def test_calcular_imc_altura_cero_lanza_error():
    with pytest.raises(ValueError, match="La altura debe ser mayor que cero."):
        calcular_imc(70, 0)

def test_calcular_imc_peso_negativo_lanza_error():
    with pytest.raises(ValueError, match="El peso debe ser mayor que cero."):
        calcular_imc(-10, 1.75)

def test_obtener_categoria_normal():
    assert obtener_categoria_imc(22.0) == "Normal"

def test_obtener_categoria_bajo_peso():
    assert obtener_categoria_imc(17.0) == "Bajo peso"

def test_obtener_categoria_sobrepeso():
    assert obtener_categoria_imc(27.0) == "Sobrepeso"

def test_obtener_categoria_obesidad():
    assert obtener_categoria_imc(32.0) == "Obesidad"
