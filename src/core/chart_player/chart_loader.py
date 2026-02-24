import json
from typing import TYPE_CHECKING

from ...util.paths import get_chart_path
from ..note import Note
from ..types import NoteDirection, ChartData, Section

if TYPE_CHECKING:
    from ..types import JsonChartData, JsonSectionData, JsonNoteData

class ChartLoader:
    """
    Clase responsable de cargar charts desde archivos JSON.
    Convierte el formato JSON a la estructura ChartData.
    """
    
    @staticmethod
    def load_chart_from_json(chart_path: str) -> ChartData:
        """Carga el Json de un Chart desde un path específico."""
        path = get_chart_path(chart_path)
        
        try:
            with open(path, encoding='utf-8') as f:
                raw_data: "JsonChartData" = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"ChartLoader: JSON inválido en {path}: {e}")
        
        # Convierte a ChartData
        return ChartLoader._parse_chart_data(raw_data)
    
    # --- PARSEO ---
    @staticmethod
    def _parse_chart_data(data: "JsonChartData") -> ChartData:
        """Convierte el diccionario raíz del JSON en un ChartData."""
        sections: list[Section] = [
            ChartLoader._parse_section(s) for s in data["sections"]
        ]
        
        return ChartData(
            song_name = data["song"], 
            bpm = data["bpm"], 
            pixels_per_ms = data["pixels_per_ms"],
            song_duration = data["song_duration"],
            total_notes = data["total_notes"],
            sections = sections
        )
    
    @staticmethod
    def _parse_section(section_data: "JsonSectionData") -> Section:
        """Convierte una sección del JSON en un objeto Section."""
        start_time = section_data["startTime"]
        end_time = section_data["endTime"]
        
        if start_time >= end_time:
            raise ValueError(
                f"ChartLoader: Sección {section_data['index']} tiene tiempos inválidos "
                f"(start: {start_time}, end: {end_time})"
            )
        
        notes: list[Note] = []
        for i, note_data in enumerate(section_data["notes"]):
            try:
                note = ChartLoader._parse_note(note_data)
                notes.append(note)
            except (KeyError, ValueError) as e:
                raise ValueError(f"ChartLoader: Error en nota #{i} de la sección {section_data['index']}: {e}")
 
        return Section(section_data["index"], start_time,end_time, notes)
    
    @staticmethod
    def _parse_note(note_data: "JsonNoteData") -> Note:
        """Convierte una nota del JSON en un objeto Note."""
        hit_time = note_data["hitTime"]
        duration = note_data["duration"]
        direction = note_data["direction"]
        
        # Validar valores
        if hit_time < 0:
            raise ValueError(f"ChartLoader: hitTime inválido: {hit_time}")
        
        if duration < 0:
            raise ValueError(f"ChartLoader: duration inválida: {duration}")
        
        if direction not in [0, 1, 2, 3]:
            raise ValueError(f"ChartLoader: direction inválida: {direction} (debe ser 0-3)")
        
        return Note(hit_time, duration, NoteDirection(direction))