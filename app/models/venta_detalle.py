from app.extensions import db
from app.models.base import TimestampMixin


class VentaDetalle(TimestampMixin, db.Model):
    __tablename__ = "venta_detalle"

    id = db.Column(db.Integer, primary_key=True)

    venta_id = db.Column(
        db.Integer,
        db.ForeignKey("ventas.id"),
        nullable=False,
        index=True
    )

    producto_id = db.Column(
        db.Integer,
        db.ForeignKey("productos.id"),
        nullable=False,
        index=True
    )

    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)

    venta = db.relationship(
        "Venta",
        back_populates="detalles"
    )

    producto = db.relationship(
        "Producto",
        back_populates="detalles_venta"
    )

    def __repr__(self):
        return f"<VentaDetalle venta_id={self.venta_id} producto_id={self.producto_id}>"