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
    usuario_id INTEGER NOT NULL,
    mes TEXT NOT NULL,
    anio TEXT NOT NULL,
    peso REAL NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES Usuarios(id)
);