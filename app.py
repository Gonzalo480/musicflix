from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib
import os

from werkzeug.utils import secure_filename


app = Flask(__name__)

app.secret_key = "clave-secreta-musicflix"


# ==========================================
# CONECTAR CON LA BASE DE DATOS
# ==========================================

def conectar_db():

    conexion = sqlite3.connect("peliculas.db")

    conexion.row_factory = sqlite3.Row

    return conexion


# ==========================================
# ENCRIPTAR CONTRASEÑA
# ==========================================

def encriptar_contrasena(contrasena):

    return hashlib.sha256(
        contrasena.encode("utf-8")
    ).hexdigest()


# ==========================================
# CREAR BASE DE DATOS
# ==========================================

def crear_db():

    conexion = conectar_db()


    # ======================================
    # TABLA CANCIONES
    # ======================================

    conexion.execute("""
        CREATE TABLE IF NOT EXISTS canciones (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            titulo TEXT NOT NULL,

            artista TEXT,

            album TEXT,

            genero TEXT,

            anio INTEGER,

            duracion INTEGER,

            calificacion REAL,

            imagen TEXT,

            audio TEXT,

            usuario_id INTEGER

        )
    """)


    # ======================================
    # COMPROBAR SI YA EXISTE usuario_id
    # ======================================

    columnas = conexion.execute(
        "PRAGMA table_info(canciones)"
    ).fetchall()


    existe_usuario_id = False


    for columna in columnas:

        if columna["name"] == "usuario_id":

            existe_usuario_id = True


    if not existe_usuario_id:

        conexion.execute(
            "ALTER TABLE canciones ADD COLUMN usuario_id INTEGER"
        )


    # ======================================
    # TABLA USUARIOS
    # ======================================

    conexion.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            usuario TEXT NOT NULL UNIQUE,

            email TEXT NOT NULL UNIQUE,

            contrasena TEXT NOT NULL

        )
    """)


    # ======================================
    # COMPROBAR CANCIONES
    # ======================================

    cantidad = conexion.execute(
        "SELECT COUNT(*) FROM canciones"
    ).fetchone()[0]


    # ======================================
    # CANCIONES DE EJEMPLO
    # ======================================

    if cantidad == 0:

        conexion.execute("""
            INSERT INTO canciones
            (
                titulo,
                artista,
                album,
                genero,
                anio,
                duracion,
                calificacion,
                imagen,
                audio
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            "Electronic Dreams",
            "Artista Demo",
            "Digital World",
            "Electrónica",
            2026,
            180,
            8.5,
            "https://images.unsplash.com/photo-1516280440614-37939bbacd81",
            "music/cancion1.mp3"

        ))


        conexion.execute("""
            INSERT INTO canciones
            (
                titulo,
                artista,
                album,
                genero,
                anio,
                duracion,
                calificacion,
                imagen,
                audio
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            "Rock Night",
            "Rock Demo",
            "Night Songs",
            "Rock",
            2025,
            210,
            8.1,
            "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f",
            "music/cancion2.mp3"

        ))


        conexion.execute("""
            INSERT INTO canciones
            (
                titulo,
                artista,
                album,
                genero,
                anio,
                duracion,
                calificacion,
                imagen,
                audio
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            "Summer Vibes",
            "Music Demo",
            "Summer",
            "Pop",
            2026,
            195,
            8.0,
            "https://images.unsplash.com/photo-1524368535928-5b5e00ddc76b",
            "music/cancion3.mp3"

        ))


        conexion.execute("""
            INSERT INTO canciones
            (
                titulo,
                artista,
                album,
                genero,
                anio,
                duracion,
                calificacion,
                imagen,
                audio
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            "Dark Sound",
            "Audio Demo",
            "Dark Music",
            "Ambient",
            2026,
            240,
            8.7,
            "https://images.unsplash.com/photo-1511379938547-c1f69419868d",
            "music/cancion4.mp3"

        ))


    conexion.commit()

    conexion.close()


# ==========================================
# INICIO / CATÁLOGO
# ==========================================

@app.route("/")
def inicio():

    conexion = conectar_db()


    canciones = conexion.execute(
        "SELECT * FROM canciones"
    ).fetchall()


    conexion.close()


    return render_template(
        "index.html",
        canciones=canciones
    )


# ==========================================
# DETALLES DE CANCIÓN
# ==========================================

@app.route("/cancion/<int:id>")
def cancion(id):

    conexion = conectar_db()


    cancion = conexion.execute(
        "SELECT * FROM canciones WHERE id = ?",
        (id,)
    ).fetchone()


    conexion.close()


    if cancion is None:

        flash(
            "La canción no existe.",
            "error"
        )

        return redirect(
            url_for("inicio")
        )


    return render_template(
        "cancion.html",
        cancion=cancion
    )


# ==========================================
# REPRODUCIR CANCIÓN
# ==========================================

@app.route("/reproducir/<int:id>")
def reproducir(id):

    # ======================================
    # COMPROBAR SESIÓN
    # ======================================

    if not session.get("usuario"):

        flash(
            "Necesitás iniciar sesión para reproducir música.",
            "error"
        )

        return redirect(
            url_for("login")
        )


    conexion = conectar_db()


    cancion = conexion.execute(
        "SELECT * FROM canciones WHERE id = ?",
        (id,)
    ).fetchone()


    conexion.close()


    if cancion is None:

        flash(
            "La canción no existe.",
            "error"
        )

        return redirect(
            url_for("inicio")
        )


    if not cancion["audio"]:

        flash(
            "Esta canción no tiene un audio asignado.",
            "error"
        )

        return redirect(
            url_for("cancion", id=id)
        )


    return render_template(
        "reproductor.html",
        cancion=cancion
    )


# ==========================================
# AGREGAR CANCIÓN
# ==========================================

@app.route("/agregar")
def agregar():

    # ======================================
    # COMPROBAR LOGIN
    # ======================================

    if not session.get("usuario"):

        flash(
            "Necesitás iniciar sesión para agregar canciones.",
            "error"
        )

        return redirect(
            url_for("login")
        )


    return render_template(
        "agregar.html"
    )


# ==========================================
# GUARDAR CANCIÓN
# ==========================================

@app.route("/guardar", methods=["POST"])
def guardar():

    # ======================================
    # COMPROBAR LOGIN
    # ======================================

    if not session.get("usuario"):

        flash(
            "Necesitás iniciar sesión.",
            "error"
        )

        return redirect(
            url_for("login")
        )


    # ======================================
    # DATOS DEL FORMULARIO
    # ======================================

    titulo = request.form["titulo"]

    artista = request.form["artista"]

    album = request.form["album"]

    genero = request.form["genero"]

    anio = request.form["anio"]

    duracion = request.form["duracion"]

    calificacion = request.form["calificacion"]

    imagen = request.form["imagen"]


    # ======================================
    # ARCHIVO MP3
    # ======================================

    archivo_audio = request.files["audio"]


    if archivo_audio.filename == "":

        flash(
            "Seleccioná un archivo MP3.",
            "error"
        )

        return redirect(
            url_for("agregar")
        )


    # ======================================
    # COMPROBAR EXTENSIÓN
    # ======================================

    nombre_archivo = secure_filename(
        archivo_audio.filename
    )


    if not nombre_archivo.lower().endswith(".mp3"):

        flash(
            "Solo se permiten archivos MP3.",
            "error"
        )

        return redirect(
            url_for("agregar")
        )


    # ======================================
    # CREAR CARPETA MUSIC
    # ======================================

    carpeta_music = os.path.join(
        app.static_folder,
        "music"
    )


    os.makedirs(
        carpeta_music,
        exist_ok=True
    )


    # ======================================
    # EVITAR ARCHIVOS REPETIDOS
    # ======================================

    nombre_original = nombre_archivo

    contador = 1


    while os.path.exists(
        os.path.join(carpeta_music, nombre_archivo)
    ):

        nombre_archivo = (
            str(contador)
            + "_"
            + nombre_original
        )

        contador += 1


    # ======================================
    # GUARDAR MP3
    # ======================================

    ruta_audio = os.path.join(
        carpeta_music,
        nombre_archivo
    )


    archivo_audio.save(
        ruta_audio
    )


    audio = "music/" + nombre_archivo


    # ======================================
    # GUARDAR EN BASE DE DATOS
    # ======================================

    conexion = conectar_db()


    conexion.execute("""
        INSERT INTO canciones
        (
            titulo,
            artista,
            album,
            genero,
            anio,
            duracion,
            calificacion,
            imagen,
            audio,
            usuario_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        titulo,
        artista,
        album,
        genero,
        anio,
        duracion,
        calificacion,
        imagen,
        audio,
        session["usuario_id"]

    ))


    conexion.commit()

    conexion.close()


    flash(
        "Canción agregada correctamente.",
        "exito"
    )


    return redirect(
        url_for("mis_canciones")
    )


# ==========================================
# MIS CANCIONES
# ==========================================

@app.route("/mis-canciones")
def mis_canciones():

    # ======================================
    # COMPROBAR LOGIN
    # ======================================

    if not session.get("usuario"):

        flash(
            "Necesitás iniciar sesión.",
            "error"
        )

        return redirect(
            url_for("login")
        )


    conexion = conectar_db()


    canciones = conexion.execute("""
        SELECT *
        FROM canciones
        WHERE usuario_id = ?
        ORDER BY id DESC
    """, (

        session["usuario_id"],

    )).fetchall()


    conexion.close()


    return render_template(
        "mis_canciones.html",
        canciones=canciones
    )


# ==========================================
# ELIMINAR CANCIÓN
# ==========================================

@app.route("/eliminar/<int:id>")
def eliminar(id):

    # ======================================
    # COMPROBAR LOGIN
    # ======================================

    if not session.get("usuario"):

        flash(
            "Necesitás iniciar sesión.",
            "error"
        )

        return redirect(
            url_for("login")
        )


    conexion = conectar_db()


    # ======================================
    # BUSCAR SOLO LA CANCIÓN DEL USUARIO
    # ======================================

    cancion = conexion.execute("""
        SELECT *
        FROM canciones
        WHERE id = ?
        AND usuario_id = ?
    """, (

        id,
        session["usuario_id"]

    )).fetchone()


    # ======================================
    # COMPROBAR PROPIETARIO
    # ======================================

    if cancion is None:

        conexion.close()


        flash(
            "No podés eliminar esta canción.",
            "error"
        )


        return redirect(
            url_for("mis_canciones")
        )


    # ======================================
    # ELIMINAR DE BASE DE DATOS
    # ======================================

    conexion.execute("""
        DELETE FROM canciones
        WHERE id = ?
        AND usuario_id = ?
    """, (

        id,
        session["usuario_id"]

    ))


    conexion.commit()

    conexion.close()


    # ======================================
    # ELIMINAR ARCHIVO MP3
    # ======================================

    if cancion["audio"]:

        ruta_audio = os.path.join(
            app.static_folder,
            cancion["audio"]
        )


        if os.path.exists(ruta_audio):

            os.remove(ruta_audio)


    flash(
        "Canción eliminada correctamente.",
        "exito"
    )


    return redirect(
        url_for("mis_canciones")
    )


# ==========================================
# REGISTRO
# ==========================================

@app.route("/registro")
def registro():

    return render_template(
        "registro.html"
    )


# ==========================================
# REGISTRAR USUARIO
# ==========================================

@app.route("/registrar", methods=["POST"])
def registrar():

    usuario = request.form["usuario"]

    email = request.form["email"]

    contrasena = request.form["contrasena"]


    contrasena_encriptada = encriptar_contrasena(
        contrasena
    )


    conexion = conectar_db()


    usuario_existente = conexion.execute(
        """
        SELECT *
        FROM usuarios
        WHERE usuario = ? OR email = ?
        """,
        (
            usuario,
            email
        )
    ).fetchone()


    if usuario_existente:

        conexion.close()


        flash(
            "El usuario o email ya existe.",
            "error"
        )


        return redirect(
            url_for("registro")
        )


    conexion.execute("""
        INSERT INTO usuarios
        (
            usuario,
            email,
            contrasena
        )
        VALUES (?, ?, ?)
    """, (

        usuario,
        email,
        contrasena_encriptada

    ))


    conexion.commit()

    conexion.close()


    flash(
        "¡Te has registrado correctamente! Ahora iniciá sesión.",
        "exito"
    )


    return redirect(
        url_for("login")
    )


# ==========================================
# LOGIN
# ==========================================

@app.route("/login")
def login():

    return render_template(
        "login.html"
    )


# ==========================================
# INICIAR SESIÓN
# ==========================================

@app.route("/iniciar", methods=["POST"])
def iniciar():

    usuario = request.form["usuario"]

    contrasena = request.form["contrasena"]


    contrasena_encriptada = encriptar_contrasena(
        contrasena
    )


    conexion = conectar_db()


    usuario_encontrado = conexion.execute(
        """
        SELECT *
        FROM usuarios
        WHERE usuario = ?
        AND contrasena = ?
        """,
        (
            usuario,
            contrasena_encriptada
        )
    ).fetchone()


    conexion.close()


    if usuario_encontrado:

        session["usuario"] = usuario_encontrado["usuario"]

        session["usuario_id"] = usuario_encontrado["id"]


        flash(
            "¡Has iniciado sesión correctamente!",
            "exito"
        )


        return redirect(
            url_for("inicio")
        )


    flash(
        "Usuario o contraseña incorrectos.",
        "error"
    )


    return redirect(
        url_for("login")
    )


# ==========================================
# CERRAR SESIÓN
# ==========================================

@app.route("/logout")
def logout():

    session.clear()


    flash(
        "Has cerrado sesión.",
        "exito"
    )


    return redirect(
        url_for("inicio")
    )


# ==========================================
# EJECUTAR APLICACIÓN
# ==========================================

if __name__ == "__main__":

    crear_db()

    app.run(debug=True)