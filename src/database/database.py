import json
from pathlib import Path
from .types import Song, Difficulty, Record, DifficultyName
from ..constants import MAX_RECORDS

class Database:
    """
    Gestiona la persistencia del juego en un archivo JSON.

    Carga el JSON al iniciar y trabaja con los modelos en memoria.
    Cuando hay un cambio relevante serializa todo y sobreescribe el JSON.

    Attributes:
        songs: Lista de canciones en memoria. El índice coincide con el id.
    """

    def __init__(self, path: Path):
        self._path = path
        self.songs: list[Song] = []

    #  CARGA Y GUARDADO
    def load(self) -> None:
        """Lee el JSON y construye los modelos en memoria."""
        with self._path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        self.songs = [self._build_song(raw) for raw in data["songs"]]

    def save(self) -> None:
        """Serializa los modelos en memoria y sobreescribe el JSON."""
        data = {"songs": [self._song_to_dict(song) for song in self.songs]}
        with self._path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    #  RECORDS                                                             #
    def save_record(self, song_id: int, difficulty_name: DifficultyName, record: Record) -> bool:
        """
        Intenta guardar un record en el top-3 de la dificultad indicada.

        Ordena por (stars DESC, points DESC). Si el record nuevo supera
        al peor del top-3 lo reemplaza. Tras guardar evalúa desbloqueos.

        Returns:
            True si el record entró al top-3, False si no.
        """
        song       = self.songs[song_id]
        difficulty = song.get_difficulty(difficulty_name)

        if difficulty is None:
            raise ValueError(f"Database: dificultad '{difficulty_name}' no encontrada en canción {song_id}.")

        records = difficulty.records
        records.sort(key=lambda r: (r.stars, r.points), reverse=True)

        entered = False

        if len(records) < MAX_RECORDS:
            records.append(record)
            records.sort(key=lambda r: (r.stars, r.points), reverse=True)
            entered = True

        elif self._is_better(record, records[-1]):
            records[-1] = record
            records.sort(key=lambda r: (r.stars, r.points), reverse=True)
            entered = True

        if entered:
            self.save()

        return entered

    #  BUILDERS — JSON → modelos
    @staticmethod
    def _build_song(raw: dict) -> Song:
        difficulties = {
            DifficultyName(name): Database._build_difficulty(DifficultyName(name), raw["difficulties"][name])
            for name in ("EASY", "NORMAL", "HARD")
        }
        return Song(
            id = raw["id"],
            name = raw["name"],
            difficulties = difficulties,
        )

    @staticmethod
    def _build_difficulty(name: DifficultyName, raw: dict) -> Difficulty:
        records = [Database._build_record(r) for r in raw["records"]]
        return Difficulty(name=name, records=records)

    @staticmethod
    def _build_record(raw: dict) -> Record:
        return Record(
            points=raw["points"],
            perfects=raw["perfects"],
            goods=raw["goods"],
            bads=raw["bads"],
            misses=raw["misses"],
            max_combo=raw["max_combo"],
            stars=raw["stars"],
            accuracy=raw["accuracy"],
            date=raw["date"],
        )

    #  SERIALIZACIÓN — modelos → JSON
    @staticmethod
    def _song_to_dict(song: Song) -> dict:
        return {
            "id":     song.id,
            "name":   song.name,
            "difficulties": {
                diff.name.value: Database._difficulty_to_dict(diff)
                for diff in song.difficulties.values()
            },
        }

    @staticmethod
    def _difficulty_to_dict(difficulty: Difficulty) -> dict:
        return {
            "records": [Database._record_to_dict(r) for r in difficulty.records]
        }

    @staticmethod
    def _record_to_dict(record: Record) -> dict:
        return {
            "points":    record.points,
            "perfects":  record.perfects,
            "goods":     record.goods,
            "bads":      record.bads,
            "misses":    record.misses,
            "max_combo": record.max_combo,
            "stars":     record.stars,
            "accuracy":  record.accuracy,
            "date":      record.date,
        }

    # ------------------------------------------------------------------ #
    #  HELPERS                                                             #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _is_better(new: Record, existing: Record) -> bool:
        """Retorna True si new supera a existing por (stars DESC, points DESC)."""
        if new.stars != existing.stars:
            return new.stars > existing.stars
        return new.points > existing.points