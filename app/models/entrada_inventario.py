from datetime import datetime

from app.extensions import db
from app.models.base import TimestampMixin


class EntradaInventario(TimestampMixin, db.Model):
    __tablename__ = "entradas_inventario"

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    producto_id = db.Column(
        db.Integer,
        db.ForeignKey("productos.id"),
        nullable=False,
        index=True
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False,
        index=True
    )

    cantidad = db.Column(db.Integer, nullable=False)
    costo_unitario = db.Column(db.Numeric(10, 2), nullable=True)
    observacion = db.Column(db.Text, nullable=True)

    producto = db.relationship(
        "Producto",
        back_populates="entradas_inventario"
    )

    usuario = db.relationship(
        "Usuario",
        back_populates="entradas_inventario"
    )

    def __repr__(self):
        return f"<EntradaInventario producto_id={self.producto_id} cantidad={self.cantidad}>"