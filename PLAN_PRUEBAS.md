# Plan de pruebas - SistemaAutenticacion

## Objetivo

Validar que la clase `SistemaAutenticacion` controle correctamente la validacion de contraseñas, el flujo de login, el bloqueo por intentos fallidos y el reinicio del estado de bloqueo.

El plan tambien busca identificar riesgos de seguridad derivados del comportamiento actual de la clase.

## Alcance

Clase bajo prueba:

- `SistemaAutenticacion`

Metodos bajo prueba:

- `validar_password(password)`
- `intentar_login(password_ingresada, password_correcta)`
- `resetear_bloqueo()`

Estados internos relevantes:

- `intentos_fallidos`
- `bloqueado`
- `MAX_INTENTOS`
- `passwords_comunes`

## Criterios de aceptacion

La clase se considera correcta para este alcance si:

- Rechaza contraseñas que no cumplen las reglas minimas.
- Acepta contraseñas validas segun las reglas implementadas.
- Incrementa el contador de intentos fallidos en logins incorrectos.
- Bloquea la cuenta al tercer intento fallido.
- Impide el acceso cuando la cuenta esta bloqueada.
- Reinicia el estado con `resetear_bloqueo()`.
- Maneja casos limite relevantes sin fallos inesperados, cuando el comportamiento actual lo permite.

## Reglas de validacion de contraseña

La contraseña debe cumplir:

- Longitud minima de 8 caracteres.
- Al menos una letra mayuscula.
- Al menos un numero.
- Al menos un caracter especial permitido: `@$!%*?&`.
- No estar en la lista de contraseñas comunes.

## Casos de prueba funcionales

| ID | Caso | Entrada | Resultado esperado |
| --- | --- | --- | --- |
| CP01 | Contraseña valida | `Password1!` | Valida |
| CP02 | Menos de 8 caracteres | `Pass1!A` | Rechazada por longitud |
| CP03 | Sin mayuscula | `password1!` | Rechazada por falta de mayuscula |
| CP04 | Sin numero | `Password!` | Rechazada por falta de numero |
| CP05 | Sin caracter especial permitido | `Password1` | Rechazada por falta de caracter especial |
| CP06 | Contraseña comun sin mayuscula | `admin123!` | Rechazada por falta de mayuscula, debido al orden actual de validacion |
| CP07 | Contraseña comun con mayuscula | `Admin123!` | Rechazada por ser comun |
| CP08 | Longitud exactamente valida | `Passw1!A` | Valida |
| CP09 | Caracter especial no permitido | `Password1#` | Rechazada |
| CP10 | Caracter especial permitido | `Password1@` | Valida |

## Casos de prueba de login

| ID | Caso | Estado inicial | Entrada | Resultado esperado |
| --- | --- | --- | --- | --- |
| CP11 | Login correcto | No bloqueado | `Password1!`, `Password1!` | Acceso concedido |
| CP12 | Login incorrecto una vez | No bloqueado | `Wrongpass1!`, `Password1!` | Intentos restantes: 2 |
| CP13 | Login incorrecto dos veces | 1 fallo previo | `Wrongpass1!`, `Password1!` | Intentos restantes: 1 |
| CP14 | Login incorrecto tercer intento | 2 fallos previos | `Wrongpass1!`, `Password1!` | Cuenta bloqueada |
| CP15 | Login correcto despues de fallos parciales | 2 fallos previos | `Password1!`, `Password1!` | Acceso concedido y contador reiniciado |
| CP16 | Login estando bloqueado | `bloqueado=True` | `Password1!`, `Password1!` | Acceso denegado |
| CP17 | Login con contraseña debil pero correcta | No bloqueado | `123456`, `123456` | Acceso concedido segun el codigo actual |
| CP18 | Login con contraseña debil incorrecta | No bloqueado | `123456`, `Password1!` | Cuenta como intento fallido |

## Casos de prueba de estado

| ID | Caso | Pasos | Resultado esperado |
| --- | --- | --- | --- |
| CP19 | Reiniciar bloqueo | Provocar 3 fallos y ejecutar `resetear_bloqueo()` | `bloqueado=False`, `intentos_fallidos=0` |
| CP20 | Reiniciar sin bloqueo previo | Ejecutar `resetear_bloqueo()` en estado limpio | Estado permanece limpio |
| CP21 | Intentos posteriores al bloqueo | Bloquear cuenta y volver a intentar | Sigue bloqueada y el contador no aumenta |
| CP22 | Login correcto reinicia contador | 2 fallos y luego login correcto | `intentos_fallidos=0` |

## Pruebas de seguridad

| ID | Riesgo | Entrada | Resultado esperado |
| --- | --- | --- | --- |
| PS01 | Contraseñas comunes | `123456`, `password`, `qwerty` | Rechazadas cuando alcanzan las validaciones necesarias |
| PS02 | Variacion de mayusculas/minusculas en comunes | `Admin123!` | Rechazada por comparacion con `lower()` |
| PS03 | Contraseña debil por patron | `Aaaaaaa1!` | Aceptada por reglas actuales, aunque es debil |
| PS04 | Payload tipo inyeccion | `"' OR '1'='1!"` | No concede acceso |
| PS05 | Entrada vacia | `""` | Rechazada |
| PS06 | Espacios al final | `Password1! ` | Aceptada por reglas actuales |
| PS07 | Contraseña muy larga | 10,000 caracteres | No debe fallar |
| PS08 | Unicode | `Contraseña1!` | Debe procesarse sin excepcion |
| PS09 | `None` como contraseña | `None` | Lanza error segun codigo actual |
| PS10 | Tipo numerico como contraseña | `12345678` | Lanza error segun codigo actual |

## Pruebas negativas

| ID | Entrada | Resultado esperado |
| --- | --- | --- |
| PN01 | `None` | Excepcion documentada por comportamiento actual |
| PN02 | Entero `12345678` | Excepcion documentada por comportamiento actual |
| PN03 | Lista `["Password1!"]` | Rechazo por longitud |
| PN04 | String vacio | Rechazo por longitud |
| PN05 | Solo espacios | Rechazo por reglas actuales |

## Prioridad de automatizacion

Prioridad alta:

- Validacion de contraseña valida.
- Rechazo por cada regla individual.
- Login exitoso.
- Tres fallos consecutivos.
- Bloqueo de cuenta.
- Reset de bloqueo.

Prioridad media:

- Entradas limite.
- Caracteres especiales.
- Contraseñas comunes.
- Contraseñas muy largas.

Prioridad alta de seguridad:

- Entrada `None`.
- Login con contraseña debil pero correcta.
- Intentos posteriores al bloqueo.
- Payload tipo inyeccion.

## Observaciones de seguridad

- `intentar_login()` valida la fortaleza de la contraseña ingresada, pero ignora el resultado.
- Una contraseña debil puede conceder acceso si coincide con `password_correcta`.
- Las contraseñas se comparan en texto plano.
- El bloqueo pertenece al objeto completo, no a un usuario especifico.
- No existe bloqueo temporal ni desbloqueo automatico.
- No hay auditoria de intentos fallidos.
- No hay control explicito de tipos de entrada.

