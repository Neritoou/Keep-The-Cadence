import json
from typing import TYPE_CHECKING

from ...util.paths import get_chart_path
from ..note import Note
from ..types import NoteDirection

from .chart_data import LoadedChart, ChartSection

if TYPE_CHECKING:
    from ..types import JsonChartData, JsonSectionData, JsonNoteData

class ChartLoader:
    """
    Clase responsable de cargar charts desde archivos JSON.
    Convierte el formato JSON a la estructura LoadedChart.
    """
    
    @staticmethod
    def load_from_song_folder(song_folder: str) -> LoadedChart:
        """
        Carga un chart desde una carpeta.
        
        Args:
            song_folder: Nombre de la carpeta.
            
        Returns:
            LoadedChart con todos los datos parseados.
            
        Raises:
            FileNotFoundError: Si la carpeta o chart no existe
            ValueError: Si el JSON está mal formado
        """
        chart_path = get_chart_path(song_folder)
        
        return ChartLoader._load_from_path(str(chart_path))
    
    @staticmethod
    def _load_from_path(chart_path: str) -> LoadedChart:
        """Carga un chart desde un path específico."""
        try:
            with open(chart_path, encoding='utf-8') as f:
                raw_data: "JsonChartData" = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"ChartLoader: Chart no encontrado en {chart_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"ChartLoader: JSON inválido en {chart_path}: {e}")
        
        # Valida estructura básica
        ChartLoader._validate_json_structure(raw_data)
        
        # Convierte a LoadedChart
        return ChartLoader._parse_chart_data(raw_data)



    # --- VALIDACIONES ---
    @staticmethod
    def _validate_json_structure(data: "JsonChartData") -> None:
        """Valida que el JSON tenga la estructura esperada."""
        required_keys = ["song", "bpm", "pixels_per_ms", "sections"]
        
        for key in required_keys:
            if key not in data:
                raise ValueError(f"ChartLoader: Falta la clave '{key}' en el JSON.")
        
        if not isinstance(data["sections"], list):
            raise ValueError("ChartLoader: 'sections' debe ser una lista.")

        if len(data["sections"]) == 0:
            raise ValueError("ChartLoader: El chart debe tener al menos una sección.")

        if not isinstance(data["sections"], list):
            raise ValueError("ChartLoader: 'sections' debe ser una lista.")
           
        if not isinstance(data["bpm"], (int, float)) or data["bpm"] <= 0:
            raise ValueError(f"ChartLoader: BPM inválido de {data['bpm']}")
        
        if not isinstance(data["pixels_per_ms"], (int, float)) or data["pixels_per_ms"] <= 0:
            raise ValueError(f"ChartLoader: pixels_per_ms inválido de {data['pixels_per_ms']}")

    @staticmethod
    def _validate_section_structure(section_data: "JsonSectionData") -> None:
        """Valida que la sección del JSON tenga la estructura esperada."""
        required_keys = ["index", "startTime", "endTime", "notes"]

        for key in required_keys:
            if key not in section_data:
                raise ValueError(f"ChartLoader: Falta la clave '{key}' en la sección.")

    @staticmethod
    def _validate_note_structure(note_data: "JsonNoteData") -> None:
        """Valida que las notas del JSON tenga la estructura esperada."""
        required_keys = ["hitTime", "duration", "direction"]

        for key in required_keys:
            if key not in note_data:
                raise KeyError(f"ChartLoader: Falta la clave '{key}' en la nota.")
            


    # --- PARSEO ---
    @staticmethod
    def _parse_chart_data(data: "JsonChartData") -> LoadedChart:
        """Convierte el JSON en LoadedChart."""
        sections: list[ChartSection] = []
        
        for section_data in data["sections"]:
            section = ChartLoader._parse_section(section_data)
            sections.append(section)

        sections.sort()

        total_duration = max(section.end_time for section in sections) if sections else 0.0

        total_notes = sum(len(section.notes) for section in sections)
        
        return LoadedChart(
            data["song"], data["bpm"], data["pixels_per_ms"],
            sections, total_duration, total_notes
        )
    
    @staticmethod
    def _parse_section(section_data: "JsonSectionData") -> ChartSection:
        """Convierte una sección JSON en ChartSection."""
        ChartLoader._validate_section_structure(section_data)

        notes: list[Note] = []
        
        for i, note_data in enumerate(section_data["notes"]):
            try:
                note = ChartLoader._parse_note(note_data)
                notes.append(note)
            except (KeyError, ValueError) as e:
                raise ValueError(f"ChartLoader Error en nota #{i} de la sección {section_data['index']}: {e}")
        
        # Ordenar notas por tiempo
        notes.sort()
        
        start_time = section_data["startTime"]
        end_time = section_data["endTime"]
        
        if start_time >= end_time:
            raise ValueError(
                f"ChartLoader: Sección {section_data['index']} tiene tiempos inválidos "
                f"(start: {start_time}, end: {end_time})"
            )

        return ChartSection(
            section_data["index"], start_time,
            end_time, notes
        )
    
    @staticmethod
    def _parse_note(note_data: "JsonNoteData") -> Note:
        """Convierte una nota del JSON en objeto Note."""
        ChartLoader._validate_note_structure(note_data)
        
        hit_time = note_data["hitTime"]
        duration = note_data["duration"]
        direction = note_data["direction"]
        
        # Validar valores
        if hit_time < 0:
            raise ValueError(f"ChartLoader: hitTime negativo: {hit_time}")
        
        if duration < 0:
            raise ValueError(f"ChartLoader: duration negativa: {duration}")
        
        if direction not in [0, 1, 2, 3]:
            raise ValueError(f"ChartLoader: direction inválida: {direction} (debe ser 0-3)")
        
        return Note(hit_time, duration, NoteDirection(direction))