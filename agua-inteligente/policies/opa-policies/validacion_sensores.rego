# Código adaptado de la carpeta ejemplos/IaC-seguridad/policies/

package planta.sensores

deny[msg] {
  input.lectura.tipo == "ph"
  input.lectura.valor < 0
  msg := "Valor de pH no puede ser negativo"
}

deny[msg] {
  input.lectura.tipo == "ph"
  input.lectura.valor > 14
  msg := "Valor de pH no puede ser mayor a 14"
}

deny[msg] {
  input.lectura.tipo == "turbidez"
  input.lectura.valor < 0
  msg := "Valor de turbidez no puede ser negativo"
}

deny[msg] {
  input.lectura.tipo == "caudal"
  input.lectura.valor < 0
  msg := "Valor de caudal no puede ser negativo"
}
