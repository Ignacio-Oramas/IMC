CREATE TABLE IF NOT EXISTS Entrenador (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dni TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    altura FLOAT NOT NULL,
    peso_inicial FLOAT NOT NULL,
    peso_ideal FLOAT,
    entrenador_id INTEGER,
    FOREIGN KEY (entrenador_id) REFERENCES Entrenador (id)
);

CREATE TABLE IF NOT EXISTS Pesos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    mes TEXT NOT NULL,
    peso FLOAT NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES Usuarios (id)
);