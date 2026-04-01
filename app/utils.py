def generar_codigo_barras_producto(producto_id: int) -> str:
    """
    Genera un código numérico de 13 dígitos para el producto.
    Ejemplo:
    producto_id=1   -> 7500000000001
    producto_id=25  -> 7500000000025
    """
    return f"750{producto_id:010d}"