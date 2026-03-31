from app.extensions import db
from app.models.base import TimestampMixin


class Categoria(TimestampMixin, db.Model):
    __tablename__ = "categorias"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False, index=True)
    descripcion = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)

    productos = db.relationship(
        "Producto",
        back_populates="categoria",
        lazy=True
    )

    def __repr__(self):
        return f"<Categoria {self.nombre}>"