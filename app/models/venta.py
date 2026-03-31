from datetime import datetime

from app.extensions import db
from app.models.base import TimestampMixin


class Venta(TimestampMixin, db.Model):
    __tablename__ = "ventas"

    id = db.Column(db.Integer, primary_key=True)
    numero_venta = db.Column(db.String(20), unique=True, nullable=False, index=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    metodo_pago = db.Column(db.String(20), nullable=False, default="efectivo")
    observacion = db.Column(db.Text, nullable=True)

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False,
        index=True
    )

    usuario = db.relationship(
        "Usuario",
        back_populates="ventas"
    )

    detalles = db.relationship(
        "VentaDetalle",
        back_populates="venta",
        cascade="all, delete-orphan",
        lazy=True
    )

    def __repr__(self):
        return f"<Venta {self.numero_venta}>"