# Examen Sustitutorio Versión A

### Alumno: Alanya Campos, Luis Alberto - 20210290J

### **Pregunta 1**

El IaC junto a policy-as-code es necesaria para la seguridad y las operaciones de nuestro sistema.

Primero, la seguridad física es importante para el proyecto, ya que evita que se hagan cambios manuales sin que estos queden registrados cuando se tiene acceso directo a los servidores. Al usar IaC declarativo, entonces cada cambio que se haga quedará registrado en git. Además, las políticas definidas validarían que nadie esté haciendo configuraciones innecesarias (por ejemplo, abrir puertos innecesarios).

Segundo, el riesgo de cambios urgentes puede ocasionar drift, generando estados diferentes entre el estado declarado y el estado real. Para estos casos, sin IaC declarativa, estos cambios que generan drift no quedan registrados para los siguientes desplieguees que se hagan. Entonces, aplicando policy-as-code, se debería tener políticas que bloqueen cambios sin aprovación, haciendo que todo cambio (por más urgente que sea) necesite una minima validación.

Tercero, la reconstrucción forense se logra gracias a la trazabilidad de los cambios, cosa que el IaC declarativa nos brinda. Con esto, cada commit tiene un autor, una fecha y una razón del cambio, haciendo más fácil así la detección del cambio que origina un error o un comportamiento no deseado. Esto va de la mano con la idempotencia, que nos garantiza recrear el estado exacto de cualquier momento del proyecto aplicando el mismo código.

Ahora, el principio del menor privilegio se relacion con los tres puntos anteriores. Se debe limitar los permisos a los mínimos necesarios. Gracias al IaC declarativa, podemos definir que ciertos roles puedan modificar políticas de red, por ejemplo. Sin esto, cualquier desarrollador/operador sin ciertas capacidades podría modificar datos sensibles, afectando la seguridad del proyecto.

- Escenario de fallo grave: Supongamos que hay un script imperativo (no verifica el estado actual del sistema), este puede ser ejecutado por un desarrollador, creando más réplicas de las declaradas y generando un comportamiento "inestable" en el sistema, ocasionando fallas operativas. Como el cambio fue manual e imperativo, entonces no hay una trazabilidad clara ni un estado deseado definido, haciendo dificil la auditoría frente a este accidente.

### **Pregunta 2**

El drift es cuando el estado real del sistema es diferente al estado declarado, y en sistemas críticos como este, puede causar problemas serios si el agua sale contaminada. 

Detección automática: Para detectar el drift necesitamos implementar detección continua. Para Kubernetes se podría usar un operador que funcionan comparando constantemente el estado del cluster con lo que está en git. Cada ciertos minutos se hace esta comparación y cuando encuentran diferencias generan eventos de drift. Para el caso que se menciona:

- Se detectaría que control-service tiene diferente número de réplicas que lo ya declarado en git
- También se vería que el networkpolicy tiene reglas que no coinciden con el manifest

Ahora, para la base de datos se podría usar un script automatizado que se ejecute cada hora y compare los parámetros de configuración de la DB con un archivo en git. Este script podría sacar la configuración actual y hacer un diff contra el archivo deseado. Las evidencias podrían ser:

- Logs en formato json con un timestamp, el recurso afectado, el cambio detectado y el hash del commit implicado.
- Un reporte automático de lo que se detectó, que se enviaría para auditoría.

Bloqueo preventivo: Acá se implementaría varias capas de seguridad. En Kubernetes, por ejemplo, se aplicaría un RBAC muy restringido, donde ningún desarrollador tenga permisos de escritura en el name space de producción. Entonces, si un operador necesitaría hacer un cambio, debería hacerlo mediante PRs en github. 

Remediación segura:

- Para control-service: Primero se verificaría que las réplicas extras no estén controlando comandos activos. Se esperaría a que estas terminen sus operaciones actuales. Luego, se eliminaría una por una. Se moniteorarían métricas de la latencia del "sensor-service" durante todo este proceso. En caso que algo salga mal, se realizaría un rollback inmediato.

- Para la NetworkPolicy: Primero se revisaría los logs para ver qué conexiones serían bloqueadas. Si en caso solo fueran conexiones de monitoreo, entonces se aplicaría directamente el cambio.

- Para la DB: Primero se evaluaría si el parámetro drift es peligroso, para aplicar reglas de seguridad inmediata. Si no lo es, se programaría para el próximo mantenimiento del sistema. Si es crítico, se evaluaría el impacto de un reseteo. Como es el caso es de una planta de tratamiento, se coordinaría con el grupo de operaciones para reducir el caudal temporalmente, se realizaría el backup inmediato antes del reseteo, se  aplicaría el cambio y por último se validaría que los servicios reconectan correctamente.

### **Pregunta 3**

Estructura de carpetas:

```
agua-inteligente
├── environments
│   ├── production
│   │   ├── terraform
│   │   └── kubernetes
├── modules
│   ├── base-infrastructure
│   ├── observability-stack
│   └── control-layer
├── policies
│   ├── opa-policies
│   └── validation-tests
└── .ci
```

La idea principal sería separar lo específico de cada environments de lo reutilizable (modules)

Reglas de PR y revisión:

- Primeramente, se debería proteger la rama main, para que nadie pushee directamente a esta rama.
- Todo PR va a necesitar un mínimo de aprobaciones, por ejemplo 1 aprobación por cada rol que existan.
- Checks obligatorios (scanero de seguridad, validación del Policy as code, etc)

Versionado de módulos:

Siguiendo las buenas prácticas, los tags a usar serían del versionado semántico "X.Y.Z". Donde "X" representaría cambios mayores, que requererían migración, "Y" sería para nuevas funcionalidades compatibles y "Z" para cambios pequeños como arreglo de bugs (que no afecten el comportamiento del sistema).

Convenciones de naming:

Los nombres deben ser descriptivos y deben comunicar su propósito. El objetivo es que cualquiera deba entender que hace cada recurso solomente leyendo su nombre, reduciendo así errores de configuración. Por ejemplo para los recursos, podrían seguir la estructura "{componente}-{función}". 

Gestión de secretos:

Nunca se debe poner secretos en git. Para este sistema local se podría usar secretos organizados por servicio o entorno, con roles/políticas bien definidos para restringir el acceso. También se podría optar por aplicar TTL a los secretos y que estos roten cada cierto momento.

Anti-patrones:

1. Módulos con mucha lógica condicional

Cuando un módulo tiene muchas variables booleanas y condicionales, se vuelve difícil entender que va a crear realmente. Esto genera problemas porque:

- No es claro el resultado final sin ejecutar todo el plan
- Se vuelve dificil saber cual es el estado esperado del sistema

Entonces, se recomiendan módulos simples y específicos. Si hay configuraciones muy distintas, es mejor usar módulos separados.

2. Estado compartido sin buena separación

Guardar el estado de muchos ervicios en un único archivo puede provocar:

- Bloqueos globales, donde un cambio puede detener a los demás
- Dificultad para trabajar en paralelo
- Rollbacks más complicados de realizar

En estos tipos de sistemas, esto puede ser un problema serio, donde un fallo en un servicio menor puede impedir o dificultar cambios de emergencia en servicios importantes.

### **Pregunta 4**

Módulo 1: Infraestructura base

Se aplicaría el patrón de infraestructura inmutable. Esto es que los recursos no se modifican directamente cuando hay cambios, sino que se reemplazan por completo. La infraestructura define los componentes fundamentales del sistema, como red, almacenamiento y configuración base, y cada versión representa un estado completo y consistente. Ahora, cuando se necesite un cambio, se crearía una nueva versión en lugar de aplicar cambios sobre lo existente.

Esto mejora la seguridad porque evita modificaciones manuales o no autorizadas. Además, es más flexible porque los rollbacks son simples, siempre se vuelve a un estado conocido y probado. Aunque al inicio el costo cognitivo es más alto debido a que implica reemplazar en lugar de corregir, a largo plazo el modelo es más simple de operar.

Módulo 2: Observabilidad

Se utiliza el patrón "sidecar", donde cada servicio tiene un componente adicional que se encargará del logging y las métricas de forma independiente. Estos componentes se ejecutan junto a los servicios principales y pueden inyectarse automáticamente en cada despliegue.

Desde el punto de vista de la seguridad, este patrón es importante porque cada servicio tiene su propio componente con permisos mínimos, lo que evitaría que un servicio comprometido pueda afectar los datos de observabilidad de otros servicios. Ahora, en términos de resiliencia, las fallas se aislarían, o sea, si el sistema central de monitoreo tiene problemas, los sidecars podrían seguir funcionando sin afectar la operación del servicio. El costo cognitivo sería bajo, ya que los desarrolladores no tendrían la necesidad de entender como funciona la observabilidad internamente, solo generan logs y el sidecar se encargaría del resto.

Módulo 3: Control opracional

Se podría aplicar el patrón adapter, ya que agrega una capa de abstracción entre la lógica de negocio y las implementaciones. Se definiría interfaces estándar para interactuar con recursos externos.

Este diseño mejora la seguridad porque todos los comandos pasan por un punto central donde pueden aplicarse ciertas validaciones, límites o políticas, todo esto antes de interactuar con recursos reales. Hablando de la resiliencia, esto permite cambiar o reemplazar tecnologías sin afectar la lógica principal del sistema. Ahora, el costo cognitivo inicial vendría a ser medio alto, debido a que se deben entender dos capas. La reutilización vendría a ser alta dentro del sistema, ya que la lógica de negocio puede mantenerse sin modificaciones mientras se cambian solamente los adapters.

### **Pregunta 5**

Para este caso, el control-service necesita obtener datos de sensor-service, pero no debe depender directamente de este. Para evitar esto, se aplica DIP, donde se depende de abstracciones y no de implementaciones concretas. Aplicando esto, el control-service solo definiría qué datos necesita y con qué frecuencia, sin importarle de dónde vienen dichos datos.

Entonces, el control-service definiría un "contrato" que describa los datos que necesita. Estos datos pueden venir del servicio en funcionamiento, de un caché, o inclusive de una base de datos. Para esto se usa un componente intermediario que intenta obtener los datos del servicio real y, si falla, recurre a diversas alternativas. Esto facilita las pruebas, mejora el aislamiento frente a ciertas fallas y permite que cada componente sea modificado/mejorado de manera independiente.

Ahora, para evitar fallas en cascada se utiliza el patrón circuit breaker. Entonces, cuando un servicio falla seguidamente, el sistema deja de llamarlo temporalmente para evitar sobrecargas, permitiendo así su recuperación. En un estado normal, las llamadas funcionan con normalidad. En caso que se supere un número ya definido de fallas consecutivas, las llamadas fallan inmediatamente. Luego de un determinado tiempo, se pasa a un estado de "prueba", donde se permiten algunas llamadas para probar si el servicio se ha recuperado por completo.

Este mecanismo se configura con variables claras, como el número de fallas antes de abrir el circuit, el tiempo máximo de espera por llamada o el período de recuperación antes de volver a intentar. Además, es importante medir el comportamiento del circuito, incluyendo su estado actual o el número de fallas consecutivas.

Ahora, en casos donde un servicio expone diversos endpoints, se podría usar el patrón facade. Este patrón nos da una interfaz simple que oculta varias operaciones internas, juntando todas en una sola llamada. Además, este componente puede unificar los resultados en una respuesta única que incluya datos, los timestamps, etc.

Por último, para que todo esto funcione correctamente, los contratos entre servicios deben estar claramente definidos. Se debe garantizar variables como latencia o comportamiento ante fallas. Ahora el sistema debe mostrar métricas. Estas pueden ser latencias, tasas de éxito y fallo o estados del circuit breaker.

### **Pregunta 6**

Las pruebas de IaC para este tipo de casos deben ser elaboradas cuidadosamente, ya que una prueba mal automatizada puede tener impactos reales. Debido a esto, no todas las pruebas se pueden automatizar y también es necesario evaluar el riesgo que tiene de cada una de estas.

Primeramente, no se debería automatizar pruebas que interactúen directamente con el hardware físico, como por ejemplo sensores reales, ni pruebas de recuperación ante fallas de infraestructura. Este tipo de pruebas pueden causar desgaste o interrupciones reales en la infraestructura, por lo que deben ejecutarse de forma manual en ambientes de simulación.

Ahora, en cada commit, se deben ejecutarse pruebas rápidas con el fin de prevenir que errores lleguen a producción. Estas pueden ser validaciones de sintaxis y linters del código de IaC, policy as code, pruebas unitarias de módulos, escaneos básicos de seguridad y detección de drift en staging.

Hablando del flakines, esto es importante para mantener el buen funcionamiento del pipeline. Se debe configurar timeouts, aplicando reintentos solo a fallas transitorias, aislamiento entre pruebas y monitoreando seguidamente aquellas pruebas que fallen de forma seguida. Aislando o corrigiendo de manera rápida las pruiebas inestables.

Ahora, el rollback según los fallos parciales debe estar bien definido. La detección de estos fallos se basaría en métricas y healthchecks, el sistema entraría en un "modo seguro" y se aplicaría el rollback de manera gradual, aplicando validaciones de estado en cada proceso, tomando en cuenta que los cambios que afectan la persistencia del sistema requerirían intervención manual debido a que nunca deben revertirse de manera automática.

Por último, también se debe incluir una prueba de caos, obviamente controlado y ejecutada en staging, esta prueba podría ser inyección de latencia o fallas de comunicación entre servicios. Esta prueba nos permitiría validar que los mecanismos de reisliencia funcionan correctamente, que el sistema se detenga de forma segura, se recupere automáticamente y mantenga la observabilidad durante estas situaciones.

### **Pregunta 7**

Docker hardening extremo

- Uso de imágenes mínimas para reducir la superficie de ataque
- Siempre que se ejecute como usuario no root
- Modo read-only para los archivos del sistema
- Aplciar multi stage build para que la imagen final del contenedor solo tenga lo necesario
- Todas las dependencias/recursos usados se almacena en un SBOM para su analisis de vulnerabilidad

Kubernetes con PSS, NetworkPolicies y RBAC

- Evitar contenedores con privilegios/permisos elevados
- Definir el NetworkPolicies con valor default-deny
- RBAC con mínimos privilegios y roles auditables
- Aplicación del pod security standards
- Uso de ServiceAcounts únicas para cada servicio

CI/CD local-first con freeze windows

- Los pipelines CI/CD en la infraestructura local
- Ejecución automática de pruebas en cada commit
- Ejecución de linters para verificación de código
- Analisis de dependencias recopiladas en SBOM en busqueda de vulnerabilidades
- Ventanas de freeze durante las operaciones críticas o mantenimientos

Estrategia de despliegue

- Por qué no canary: Porque no es posible dividir el tráfico con el hardware real, debido a que se usa un estado físico compartido, un error puede afectar a todo el sistema.
- Por qué sí Blue-Green: Porque se tendría dos entornos (actual y nueva), donde el nuevo entorno podría operar inicialmente sin un control físico. Además nos permite un rollback inmediato cambiando de entorno.

Alertas que protejan infraestructura física

- Frecuencia anormal de los comandos físicos
- Pérdida de señales/notificaciones de sensores principales
- Accesos no autorizados o fuera de horario
- Detección de comandos diferentes a lo ya establecido
