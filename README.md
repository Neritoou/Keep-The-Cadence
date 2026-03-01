# Keep-The-Cadence
<div align="center">

#  Keep The Cadence

**🎵 Un juego de ritmo inspirado en Friday Night Funkin' 🎵**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.x-00B140?style=for-the-badge&logo=python&logoColor=white)](https://www.pygame.org/)
[![Status](https://img.shields.io/badge/Estado-Completado-success?style=for-the-badge)]()
[![Materia](https://img.shields.io/badge/Materia-Objetos%20%26%20Abstracción-purple?style=for-the-badge)]()

</div>

---

## 📖 Sobre el Proyecto

**Keep The Cadence** es un juego de ritmo desarrollado como **módulo final** para la materia de **Objetos y Abstracción de Datos** — Grupo 4.

El juego está construido en Python y captura la esencia de los juegos de ritmo clásicos: seguir el beat, no perder el tiempo, y *mantener la cadencia*. El jugador debe presionar las flechas correctas al ritmo de la música, controlado por un sistema de notas que descienden (o ascienden) por la pantalla.

> *"El ritmo no espera — ¿puedes seguirle el paso?"*

---

## 🎮 Características

- 🎶 **Sistema de Charts** — Notas sincronizadas con la música, con soporte para *tap notes* y *hold notes*
- 🏆 **Sistema de Juicios** — Perfect / Good / Bad / Miss con diferentes ventanas de timing
- 🗂️ **Selección de Canciones** — Menú de selección con vista previa de audio
- ⚙️ **Editor de Charts** — Editor interno para crear y exportar charts en JSON
- 🎨 **Interfaz completa** — Menú principal, opciones, créditos y pantalla de resultados
- 🔊 **Gestión de Audio** — Música de fondo, efectos de sonido y control de volumen

---

## 🚀 Instalación

### Requisitos Previos

Antes de instalar, asegúrate de tener:

- **Python 3.11+** — [Descargar aquí](https://www.python.org/downloads/)
- **pip actualizado:**
  ```bash
  python -m pip install --upgrade pip
  ```

### Paso 1: Instalar `enfocate` (dependencia principal)

Este proyecto utiliza [**enfocate-core-lib**](https://github.com/alecsoc/enfocate-core-lib), un framework base desarrollado por el equipo. Debes instalarlo antes de ejecutar el juego.

```bash
git clone https://github.com/alecsoc/enfocate-core-lib.git
cd enfocate-core-lib
pip install -e .
```

> ⚠️ **No olvides el punto `.` al final del comando.** Esto le indica a Python que instale el paquete desde la carpeta actual. Si todo salió bien, podrás usar `import enfocate` en cualquier archivo Python de tu sistema.

### Paso 2: Clonar el repositorio del juego

```bash
git clone https://github.com/Neritoou/Keep-The-Cadence.git
cd Keep-The-Cadence
```

### Paso 3: Instalar dependencias y ejecutar

```bash
pip install -r requirements.txt
python main.py
```

---

## 👥 Equipo de Desarrollo

<div align="center">

| Desarrollador | Rol |
|---------------|-----|
| **Odett Sayegh** | Desarrollo |
| **Agostinho Dos Santos** | Desarrollo |
| **Angel Ramirez** | Desarrollo |

*Grupo 4 — Materia: Objetos y Abstracción de Datos*

</div>

---

## 🙏 Agradecimientos

Un enorme gracias a todas las personas que hicieron posible este proyecto:

### 🎵 Charts
Gracias a quienes se tomaron el tiempo de crear y ajustar los charts del juego:

- **Joce Arepa**
- **Reptil Político**

### 🎨 Diseño
- **Andrea Zabala** — Diseño visual del juego

### 🖼️ Assets de Miku — FNF Mods

Los sprites y assets utilizados para el personaje de **Hatsune Miku** fueron obtenidos de dos mods de la comunidad de **Friday Night Funkin'**. Todo el crédito por dichos assets pertenece a sus respectivos creadores. ¡Si te gustan, visítalos y apóyalos!

<div align="center">

| Mod | Link |
|-----|------|
| 🎤 Mod 1 | [Ver en GameBanana](https://gamebanana.com/mods/485992) |
| 🎤 Mod 2 | [Ver en GameBanana](https://gamebanana.com/mods/44307) |

</div>

---

## 📚 Contexto Académico

Este proyecto fue desarrollado como parte del módulo evaluativo de la materia **Objetos y Abstracción de Datos**, con el objetivo de aplicar conceptos de:

- Programación Orientada a Objetos (POO)
- Abstracción y encapsulamiento
- Patrones de diseño (State Machine, Factory, etc.)
- Gestión de recursos y arquitectura de software

---

<div align="center">

*Hecho con 💜 — Grupo 4*

</div>
