# Analisis de resultados de pruebas - SistemaAutenticacion

## Resultado general

Se ejecuto la suite automatizada con `pytest` sobre la clase `SistemaAutenticacion`.

Resultado:

```text
28 passed in 0.67s
```

Resumen:

- Pruebas ejecutadas: 28
- Pruebas pasadas: 28
- Pruebas fallidas: 0
- Estado general: exitoso

La implementacion actual cumple con los casos de prueba automatizados definidos. Esto confirma que el codigo se comporta de acuerdo con las expectativas documentadas en la suite.

## Interpretacion del resultado

El hecho de que todas las pruebas pasen no significa que el sistema sea seguro para produccion. Significa que el comportamiento actual esta cubierto por los tests y que no se detectaron regresiones contra las expectativas definidas.

Algunos tests documentan comportamientos que funcionan segun el codigo actual, pero que representan riesgos desde una perspectiva de seguridad. El caso mas importante es que una contraseña debil pero correcta concede acceso porque `intentar_login()` ignora el resultado de `validar_password()`.

## Vulnerabilidades o riesgos no cubiertos completamente

Las pruebas actuales no cubren o solo cubren parcialmente los siguientes riesgos:

- Fuerza bruta distribuida por usuario, direccion IP o dispositivo.
- Bloqueo temporal con expiracion automatica.
- Almacenamiento seguro de contraseñas.
- Uso de hashing, salting o algoritmos como `bcrypt`, `argon2` o `pbkdf2`.
- Comparacion segura contra ataques de tiempo.
- Auditoria y registro de eventos de seguridad.
- Separacion del estado de bloqueo por usuario.
- Pruebas de concurrencia con intentos simultaneos.
- Politicas avanzadas de contraseña, como deteccion de patrones simples.
- Normalizacion de espacios al inicio o final de la contraseña.
- Manejo robusto y controlado de tipos invalidos.

## Hallazgos relevantes

### 1. Login con contraseña debil pero correcta

El metodo `intentar_login()` llama a `validar_password()`, pero no usa el resultado para bloquear el flujo de autenticacion.

Impacto:

- Una contraseña como `123456` puede conceder acceso si coincide con `password_correcta`.
- Esto contradice una politica estricta de contraseñas si se espera que todas las credenciales activas sean robustas.

Nivel de riesgo: medio, o alto si el sistema permite establecer contraseñas debiles.

### 2. Comparacion de contraseñas en texto plano

El metodo compara:

```python
password_ingresada == password_correcta
```

Impacto:

- Sugiere que la contraseña correcta puede estar almacenada o manejada en texto plano.
- No hay hashing ni proteccion criptografica.

Nivel de riesgo: alto en un sistema real.

### 3. Bloqueo global por instancia

El estado `intentos_fallidos` y `bloqueado` pertenece al objeto `SistemaAutenticacion`, no a un usuario concreto.

Impacto:

- Un usuario podria bloquear el sistema completo si la instancia se comparte.
- No se puede diferenciar el historial de intentos por cuenta.

Nivel de riesgo: medio.

### 4. Falta de control explicito de tipos

Entradas como `None` o numeros producen excepciones.

Impacto:

- El sistema puede fallar si recibe entradas no esperadas.
- En una API o interfaz real, esto podria convertirse en errores 500 o denegacion de servicio parcial.

Nivel de riesgo: medio.

### 5. Sin auditoria de seguridad

No hay registro de intentos fallidos, bloqueos ni desbloqueos.

Impacto:

- Dificulta detectar ataques de fuerza bruta.
- Dificulta investigar incidentes.

Nivel de riesgo: medio.

## Sugerencias de mejora para el codigo original

### Validar tipos de entrada

Agregar validacion explicita antes de aplicar reglas:

```python
if not isinstance(password, str):
    return False, "La contraseña debe ser texto."
```

Esto evita excepciones no controladas y mejora la robustez.

### Separar validacion de contraseña y autenticacion

La validacion de fortaleza deberia usarse al crear o cambiar una contraseña. El login deberia verificar credenciales ya registradas.

Si se desea impedir contraseñas debiles tambien en login, el resultado de `validar_password()` debe usarse explicitamente:

```python
es_valida, mensaje = self.validar_password(password_ingresada)
if not es_valida:
    return False, mensaje
```

### Usar hashing seguro

No comparar ni almacenar contraseñas en texto plano. Usar un algoritmo diseñado para contraseñas:

- `argon2`
- `bcrypt`
- `pbkdf2_hmac`

### Usar comparacion segura

Si se comparan secretos, usar una comparacion resistente a diferencias de tiempo:

```python
import hmac

hmac.compare_digest(password_ingresada, password_correcta)
```

### Manejar intentos por usuario

Reemplazar el contador global por una estructura asociada a usuarios:

```python
self.intentos_fallidos_por_usuario = {}
self.bloqueos_por_usuario = {}
```

### Agregar bloqueo temporal

El bloqueo deberia tener expiracion:

- 5 minutos para primeros bloqueos.
- Incremento progresivo si se repite el ataque.
- Registro del momento del bloqueo.

### Registrar eventos de seguridad

Registrar:

- Login exitoso.
- Login fallido.
- Bloqueo de cuenta.
- Reinicio de bloqueo.
- Entradas invalidas.

### Definir politica de espacios

Actualmente `Password1! ` es valida. Se debe decidir si:

- Se permite como caracter real de la contraseña.
- Se rechaza.
- Se aplica `strip()` antes de validar.

Para seguridad, no conviene modificar silenciosamente la contraseña durante login. Si se define una politica, debe aplicarse de forma consistente.

## Recomendaciones de pruebas futuras

Agregar pruebas para:

- Hashing y verificacion de hashes.
- Bloqueo por usuario.
- Expiracion del bloqueo.
- Intentos simultaneos.
- Auditoria de eventos.
- Politicas contra contraseñas conocidas.
- Contraseñas con espacios al inicio.
- Contraseñas con caracteres Unicode complejos.
- Pruebas con Hypothesis para generar entradas aleatorias.

## Resumen ejecutivo

Se ejecutaron 28 pruebas automatizadas sobre la clase `SistemaAutenticacion`, todas con resultado exitoso. Las pruebas validan las reglas principales de contraseña, el flujo de autenticacion, el bloqueo tras tres intentos fallidos, el reinicio del bloqueo y varios casos limite.

El resultado demuestra que la clase funciona conforme a la implementacion actual. Sin embargo, el analisis de seguridad identifica debilidades importantes: comparacion de contraseñas en texto plano, ausencia de hashing, bloqueo no asociado a usuarios, falta de auditoria, ausencia de bloqueo temporal y manejo incompleto de entradas invalidas.

Conclusion: la clase es adecuada como ejercicio academico o prototipo basico, pero requiere mejoras sustanciales antes de usarse en un entorno real donde la seguridad de autenticacion sea relevante.

