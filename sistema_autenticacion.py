import re


class SistemaAutenticacion:
    def __init__(self):
        self.intentos_fallidos = 0
        self.bloqueado = False
        self.MAX_INTENTOS = 3
        self.passwords_comunes = ["123456", "password", "admin123", "qwerty", "admin123!"]

    def validar_password(self, password):
        """
        Verifica que la contraseña cumpla con:
        - Longitud mínima de 8 caracteres.
        - Al menos una mayúscula.
        - Al menos un número.
        - Al menos un carácter especial (@$!%*?&).
        - No ser una contraseña común.
        """
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres."

        if not any(c.isupper() for c in password):
            return False, "La contraseña debe tener al menos una mayúscula."

        if not any(c.isdigit() for c in password):
            return False, "La contraseña debe tener al menos un número."

        if not re.search(r"[@$!%*?&]", password):
            return False, "La contraseña debe tener al menos un carácter especial (@$!%*?&)."

        if password.lower() in self.passwords_comunes:
            return False, "La contraseña es demasiado común."

        return True, "Contraseña válida."

    def intentar_login(self, password_ingresada, password_correcta):
        """
        Simula un intento de login con manejo de bloqueo.
        """
        if self.bloqueado:
            return False, "Cuenta bloqueada por demasiados intentos fallidos."

        # Primero validamos la fortaleza de la contraseña ingresada (opcional en login, pero útil según requerimiento)
        es_valida, mensaje = self.validar_password(password_ingresada)
        if not es_valida:
            # Podríamos contar esto como intento fallido o simplemente advertir
            pass

        if password_ingresada == password_correcta:
            self.intentos_fallidos = 0
            return True, "Acceso concedido."
        else:
            self.intentos_fallidos += 1
            if self.intentos_fallidos >= self.MAX_INTENTOS:
                self.bloqueado = True
                return False, "Contraseña incorrecta. Cuenta bloqueada."
            return False, f"Contraseña incorrecta. Intentos restantes: {self.MAX_INTENTOS - self.intentos_fallidos}"

    def resetear_bloqueo(self):
        self.intentos_fallidos = 0
        self.bloqueado = False