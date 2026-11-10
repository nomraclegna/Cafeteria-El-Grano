class ErrorNegocio(Exception):
    status_code = 400

    def __init__(self, mensaje: str):
        super().__init__(mensaje)
        self.mensaje = mensaje


class ReglaNegocioError(ErrorNegocio):
    status_code = 400


class CredencialesInvalidasError(ErrorNegocio):
    status_code = 401


class AccesoDenegadoError(ErrorNegocio):
    status_code = 403


class NoEncontradoError(ErrorNegocio):
    status_code = 404


class ConflictoError(ErrorNegocio):
    status_code = 409
