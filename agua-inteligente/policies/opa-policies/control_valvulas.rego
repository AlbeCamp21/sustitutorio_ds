# Código adaptado de la carpeta ejemplos/IaC-seguridad/policies/

package planta.control

deny[msg] {
  input.comando.valvula == "emergencia"
  input.comando.accion == "abrir"
  count(input.alarmas_activas) == 0
  msg := "No se puede abrir valvula de emergencia sin alarmas activas"
}

deny[msg] {
  input.comando.valvula == "emergencia"
  input.comando.accion == "cerrar"
  count(input.alarmas_activas) > 0
  msg := "No se puede cerrar valvula de emergencia con alarmas activas"
}
