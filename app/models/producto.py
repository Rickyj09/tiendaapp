from app.extensions import db
from app.models.base import TimestampMixin


class Producto(TimestampMixin, db.Model):
    __tablename__ = "productos"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(30), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(150), nullable=False, index=True)
    descripcion = db.Column(db.Text, nullable=True)

    categoria_id = db.Column(
        db.Integer,
        db.ForeignKey("categorias.id"),
        nullable=False,
        index=True
    )

    precio_venta = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    costo = db.Column(db.Numeric(10, 2), nullable=True)
    stock_actual = db.Column(db.Integer, nullable=False, default=0)
    stock_minimo = db.Column(db.Integer, nullable=False, default=0)
    unidad_medida = db.Column(db.String(30), nullable=True)
    codigo_barras = db.Column(db.String(50), unique=True, nullable=True, index=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)

    categoria = db.relationship(
        "Categoria",
        back_populates="productos"
    )

    entradas_inventario = db.relationship(
        "EntradaInventario",
        back_populates="producto",
        lazy=True
    )

    detalles_venta = db.relationship(
        "VentaDetalle",
        back_populates="producto",
        lazy=True
    )

    def __repr__(self):
        return f"<Producto {self.codigo} - {self.nombre}>"