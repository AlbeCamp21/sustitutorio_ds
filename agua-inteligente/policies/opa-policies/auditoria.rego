# Código adaptado de la carpeta ejemplos/IaC-seguridad/policies/

package planta.auditoria

deny[msg] {
  not input.operacion
  msg := "Operacion debe estar presente en registro de auditoria"
}

deny[msg] {
  input.operacion == ""
  msg := "Operacion no puede estar vacia"
}
