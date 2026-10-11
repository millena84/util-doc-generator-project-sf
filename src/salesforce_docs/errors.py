"""Exceções do utilitário."""


class DocsGeneratorError(Exception):
    """Erro base."""


class ConfigError(DocsGeneratorError):
    """Configuração global inválida: interrompe a execução."""


class GlobalFailure(DocsGeneratorError):
    """Falha global (CLI, autenticação, sessão): interrompe a execução."""

    def __init__(self, code, message, suggestion=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.suggestion = suggestion


class SessionExpiredError(DocsGeneratorError):
    """INVALID_SESSION_ID / HTTP 401: salvar estado e interromper."""

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class CliNotFoundError(DocsGeneratorError):
    """Executável `sf` não encontrado no PATH."""
