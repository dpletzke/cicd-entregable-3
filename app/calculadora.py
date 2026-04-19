"""Basic arithmetic operations used by the calculator app."""

AUTOR = "Grupo 1!!!!"


def sumar(a, b):
    """Return the sum of two numbers."""
    return a + b


def restar(a, b):
    """Return the difference between two numbers."""
    return a - b


def multiplicar(a, b):
    """Return the product of two numbers."""
    return a * b


def dividir(a, b):
    """Return the quotient of two numbers.

    Raises:
        ZeroDivisionError: If ``b`` is zero.
    """
    if b == 0:
        raise ZeroDivisionError("No se puede dividir por cero")
    return a / b
