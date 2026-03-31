from app import create_app
from app.extensions import db
from app.models.usuario import Usuario

app = create_app()

with app.app_context():
    username = "admin"

    usuario = Usuario.query.filter_by(username=username).first()

    if usuario:
        print(f"El usuario '{username}' ya existe.")
    else:
        nuevo_usuario = Usuario(
            nombre="Administrador",
            username="admin",
            activo=True
        )
        nuevo_usuario.set_password("Admin123*")

        db.session.add(nuevo_usuario)
        db.session.commit()

        print("Usuario administrador creado correctamente.")
        print("Usuario: admin")
        print("Clave: Admin123*")