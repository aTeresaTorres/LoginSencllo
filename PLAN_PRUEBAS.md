# Plan de pruebas ejecutado - SistemaAutenticacion

## Objetivo

Validar el comportamiento real de la clase `SistemaAutenticacion` mediante la suite automatizada `pytest` incluida en `test_sistema_autenticacion.py`.

Este documento describe unicamente las pruebas que realmente fueron implementadas y ejecutadas.

## Alcance

Clase bajo prueba:

- `SistemaAutenticacion`

Metodos bajo prueba:

- `validar_password(password)`
- `intentar_login(password_ingresada, password_correcta)`
- `resetear_bloqueo()`

Estados internos verificados:

- `intentos_fallidos`
- `bloqueado`
- `MAX_INTENTOS`

## Resumen de cobertura ejecutada

| Area | Cantidad de pruebas ejecutadas |
| --- | ---: |
| Validacion de passwords invalidas | 8 |
| Validacion de passwords validas | 5 |
| Entradas no string o no convencionales | 3 |
| Flujo de login y bloqueo | 8 |
| Reset de bloqueo | 2 |
| Casos de seguridad y limite adicionales | 2 |
| **Total** | **28** |

## Casos de prueba ejecutados

### Validacion de passwords invalidas

Estos casos corresponden al test parametrizado `test_validar_password_rechaza_passwords_invalidas`.

| ID | Entrada | Resultado esperado |
| --- | --- | --- |
| VP-01 | `Pass1!A` | Rechazo por tener menos de 8 caracteres |
| VP-02 | `password1!` | Rechazo por no tener mayuscula |
| VP-03 | `Password!` | Rechazo por no tener numero |
| VP-04 | `Password1` | Rechazo por no tener caracter especial permitido |
| VP-05 | `admin123!` | Rechazo por no tener mayuscula |
| VP-06 | `Admin123!` | Rechazo por ser una contrasena comun |
| VP-07 | `Password1#` | Rechazo por usar un caracter especial no permitido |
| VP-08 | `""` | Rechazo por longitud menor a 8 caracteres |

Cantidad ejecutada: 8.

### Validacion de passwords validas segun reglas actuales

Estos casos corresponden al test parametrizado `test_validar_password_acepta_passwords_validas_segun_reglas_actuales`.

| ID | Entrada | Resultado esperado |
| --- | --- | --- |
| VP-09 | `Password1!` | Password valida |
| VP-10 | `Passw1!A` | Password valida |
| VP-11 | `Password1@` | Password valida |
| VP-12 | `Contrasena1!` con caracter Unicode en el archivo de prueba | Password valida |
| VP-13 | `Password1! ` | Password valida segun reglas actuales, aunque tenga espacio final |

Cantidad ejecutada: 5.

### Entradas no string o no convencionales

| ID | Test | Entrada | Resultado esperado |
| --- | --- | --- | --- |
| EN-01 | `test_validar_password_con_entradas_no_string_lanza_error` | `None` | Lanza `TypeError` o `AttributeError` |
| EN-02 | `test_validar_password_con_entradas_no_string_lanza_error` | `12345678` | Lanza `TypeError` o `AttributeError` |
| EN-03 | `test_validar_password_con_lista_rechaza_por_longitud` | `["Password1!"]` | Rechazo por longitud |

Cantidad ejecutada: 3.

### Login, intentos fallidos y bloqueo

| ID | Test | Escenario | Resultado esperado |
| --- | --- | --- | --- |
| LG-01 | `test_intentar_login_con_password_correcta_concede_acceso_y_reinicia_intentos` | Login correcto con 2 fallos previos | Acceso concedido, contador en 0 y cuenta no bloqueada |
| LG-02 | `test_intentar_login_incorrecto_incrementa_intentos_y_muestra_restantes` | Primer login incorrecto | Acceso denegado, contador en 1 e intentos restantes en 2 |
| LG-03 | `test_intentar_login_bloquea_cuenta_en_tercer_fallo` | Tercer login incorrecto consecutivo | Cuenta bloqueada y contador igual a `MAX_INTENTOS` |
| LG-04 | `test_intentar_login_no_permite_acceso_si_la_cuenta_esta_bloqueada` | Login correcto con cuenta ya bloqueada | Acceso denegado por bloqueo |
| LG-05 | `test_intentar_login_correcto_despues_de_fallos_parciales_reinicia_contador` | Login correcto despues de 2 fallos | Acceso concedido y contador reiniciado |
| LG-06 | `test_intentar_login_password_debil_pero_correcta_concede_acceso_segun_codigo_actual` | Password debil pero correcta | Acceso concedido segun el codigo actual |
| LG-07 | `test_intentar_login_password_debil_e_incorrecta_cuenta_como_fallo` | Password debil e incorrecta | Acceso denegado y contador incrementado |
| LG-08 | `test_intentos_posteriores_al_bloqueo_no_aumentan_contador` | Intento posterior al bloqueo | Cuenta sigue bloqueada y contador no aumenta |

Cantidad ejecutada: 8.

### Reset de bloqueo

| ID | Test | Escenario | Resultado esperado |
| --- | --- | --- | --- |
| RB-01 | `test_resetear_bloqueo_reinicia_estado_bloqueado` | Reset despues de provocar bloqueo | `intentos_fallidos=0` y `bloqueado=False` |
| RB-02 | `test_resetear_bloqueo_en_estado_limpio_mantiene_estado_limpio` | Reset sin bloqueo previo | Estado permanece limpio |

Cantidad ejecutada: 2.

### Casos de seguridad y limite adicionales

| ID | Test | Entrada o escenario | Resultado esperado |
| --- | --- | --- | --- |
| SG-01 | `test_validar_password_muy_larga_no_falla` | Password de mas de 10,000 caracteres | Validacion exitosa sin excepcion |
| SG-02 | `test_intentar_login_con_payload_tipo_inyeccion_no_concede_acceso` | Payload `"' OR '1'='1!"` | Acceso denegado y contador incrementado |

Cantidad ejecutada: 2.

## Total de pruebas

La suite contiene 16 funciones de test, pero varias estan parametrizadas. Pytest ejecuto 28 pruebas individuales:

- 8 casos parametrizados de passwords invalidas.
- 5 casos parametrizados de passwords validas.
- 2 casos parametrizados de entradas no string.
- 13 tests individuales adicionales.

Total:

```text
8 + 5 + 2 + 13 = 28
```

## Casos no incluidos en este plan ejecutado

Los siguientes puntos se consideran recomendaciones futuras, no pruebas ejecutadas en la suite actual:

- Fuerza bruta distribuida por usuario o IP.
- Bloqueo temporal con expiracion automatica.
- Hashing y salting de contrasenas.
- Comparacion segura con `hmac.compare_digest`.
- Auditoria o logging de eventos de seguridad.
- Pruebas de concurrencia.
- Manejo de multiples usuarios.
- Politicas avanzadas contra patrones debiles.

## Criterio de aceptacion de la ejecucion

La ejecucion se considera exitosa si las 28 pruebas individuales pasan sin errores ni fallos.

Resultado observado:

```text
28 passed
```
