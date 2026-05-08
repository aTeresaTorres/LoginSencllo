import unicodedata

import pytest

from main import SistemaAutenticacion


@pytest.fixture
def sistema():
    return SistemaAutenticacion()


@pytest.mark.parametrize(
    ("password", "mensaje_esperado"),
    [
        ("Pass1!A", "al menos 8 caracteres"),
        ("password1!", "al menos una mayuscula"),
        ("Password!", "al menos un numero"),
        ("Password1", "al menos un caracter especial"),
        ("admin123!", "al menos una mayuscula"),
        ("Admin123!", "demasiado comun"),
        ("Password1#", "al menos un caracter especial"),
        ("", "al menos 8 caracteres"),
    ],
)
def test_validar_password_rechaza_passwords_invalidas(sistema, password, mensaje_esperado):
    es_valida, mensaje = sistema.validar_password(password)

    assert es_valida is False
    assert mensaje_esperado in _normalizar(mensaje)


@pytest.mark.parametrize(
    "password",
    [
        "Password1!",
        "Passw1!A",
        "Password1@",
        "Contraseña1!",
        "Password1! ",
    ],
)
def test_validar_password_acepta_passwords_validas_segun_reglas_actuales(sistema, password):
    es_valida, mensaje = sistema.validar_password(password)

    assert es_valida is True
    assert _normalizar(mensaje) == "contrasena valida."


@pytest.mark.parametrize(
    "password",
    [
        None,
        12345678,
    ],
)
def test_validar_password_con_entradas_no_string_lanza_error(sistema, password):
    with pytest.raises((TypeError, AttributeError)):
        sistema.validar_password(password)


def test_validar_password_con_lista_rechaza_por_longitud(sistema):
    es_valida, mensaje = sistema.validar_password(["Password1!"])

    assert es_valida is False
    assert "al menos 8 caracteres" in _normalizar(mensaje)


def test_intentar_login_con_password_correcta_concede_acceso_y_reinicia_intentos(sistema):
    sistema.intentos_fallidos = 2

    acceso, mensaje = sistema.intentar_login("Password1!", "Password1!")

    assert acceso is True
    assert mensaje == "Acceso concedido."
    assert sistema.intentos_fallidos == 0
    assert sistema.bloqueado is False


def test_intentar_login_incorrecto_incrementa_intentos_y_muestra_restantes(sistema):
    acceso, mensaje = sistema.intentar_login("Wrongpass1!", "Password1!")

    assert acceso is False
    assert _normalizar(mensaje) == "contrasena incorrecta. intentos restantes: 2"
    assert sistema.intentos_fallidos == 1
    assert sistema.bloqueado is False


def test_intentar_login_bloquea_cuenta_en_tercer_fallo(sistema):
    for _ in range(2):
        acceso, _ = sistema.intentar_login("Wrongpass1!", "Password1!")
        assert acceso is False

    acceso, mensaje = sistema.intentar_login("Wrongpass1!", "Password1!")

    assert acceso is False
    assert _normalizar(mensaje) == "contrasena incorrecta. cuenta bloqueada."
    assert sistema.intentos_fallidos == sistema.MAX_INTENTOS
    assert sistema.bloqueado is True


def test_intentar_login_no_permite_acceso_si_la_cuenta_esta_bloqueada(sistema):
    sistema.bloqueado = True
    sistema.intentos_fallidos = sistema.MAX_INTENTOS

    acceso, mensaje = sistema.intentar_login("Password1!", "Password1!")

    assert acceso is False
    assert _normalizar(mensaje) == "cuenta bloqueada por demasiados intentos fallidos."
    assert sistema.intentos_fallidos == sistema.MAX_INTENTOS
    assert sistema.bloqueado is True


def test_intentar_login_correcto_despues_de_fallos_parciales_reinicia_contador(sistema):
    sistema.intentar_login("Wrongpass1!", "Password1!")
    sistema.intentar_login("Otherwrong1!", "Password1!")

    acceso, mensaje = sistema.intentar_login("Password1!", "Password1!")

    assert acceso is True
    assert mensaje == "Acceso concedido."
    assert sistema.intentos_fallidos == 0
    assert sistema.bloqueado is False


def test_intentar_login_password_debil_pero_correcta_concede_acceso_segun_codigo_actual(sistema):
    acceso, mensaje = sistema.intentar_login("123456", "123456")

    assert acceso is True
    assert mensaje == "Acceso concedido."
    assert sistema.intentos_fallidos == 0
    assert sistema.bloqueado is False


def test_intentar_login_password_debil_e_incorrecta_cuenta_como_fallo(sistema):
    acceso, mensaje = sistema.intentar_login("123456", "Password1!")

    assert acceso is False
    assert _normalizar(mensaje) == "contrasena incorrecta. intentos restantes: 2"
    assert sistema.intentos_fallidos == 1
    assert sistema.bloqueado is False


def test_intentos_posteriores_al_bloqueo_no_aumentan_contador(sistema):
    for _ in range(3):
        sistema.intentar_login("Wrongpass1!", "Password1!")

    acceso, mensaje = sistema.intentar_login("Wrongpass1!", "Password1!")

    assert acceso is False
    assert _normalizar(mensaje) == "cuenta bloqueada por demasiados intentos fallidos."
    assert sistema.intentos_fallidos == sistema.MAX_INTENTOS
    assert sistema.bloqueado is True


def test_resetear_bloqueo_reinicia_estado_bloqueado(sistema):
    for _ in range(3):
        sistema.intentar_login("Wrongpass1!", "Password1!")

    sistema.resetear_bloqueo()

    assert sistema.intentos_fallidos == 0
    assert sistema.bloqueado is False


def test_resetear_bloqueo_en_estado_limpio_mantiene_estado_limpio(sistema):
    sistema.resetear_bloqueo()

    assert sistema.intentos_fallidos == 0
    assert sistema.bloqueado is False


def test_validar_password_muy_larga_no_falla(sistema):
    password = "A" + ("a" * 10000) + "1!"

    es_valida, mensaje = sistema.validar_password(password)

    assert es_valida is True
    assert _normalizar(mensaje) == "contrasena valida."


def test_intentar_login_con_payload_tipo_inyeccion_no_concede_acceso(sistema):
    acceso, mensaje = sistema.intentar_login("' OR '1'='1!", "Password1!")

    assert acceso is False
    assert _normalizar(mensaje) == "contrasena incorrecta. intentos restantes: 2"
    assert sistema.intentos_fallidos == 1


def _normalizar(texto):
    texto_normalizado = unicodedata.normalize("NFD", texto.lower())
    return "".join(
        caracter
        for caracter in texto_normalizado
        if unicodedata.category(caracter) != "Mn"
    )
