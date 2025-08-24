"""Abstract base class for defect detectors."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from defect_identifier.defect import Defect


@dataclass
class DetectionResult:
    """Encapsulates the result of a defect detection."""
    
    defect_name: str
    is_defective: bool
    warnings: List[str]
    locations: List[str]
    severity: str = "medium"
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "defect_name": self.defect_name,
            "is_defective": self.is_defective,
            "warnings": self.warnings,
            "locations": self.locations,
            "severity": self.severity,
            "description": self.description
        }


class DefectDetector(ABC):
    """Abstract base class for all defect detectors."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
    
    @abstractmethod
    def detect(self, source_map, problematic_pcs: List[int]) -> DetectionResult:
        """
        Detect defects based on problematic program counters.
        
        Args:
            source_map: Source map for code location mapping
            problematic_pcs: List of problematic program counters
            
        Returns:
            DetectionResult containing detection information
        """
        pass
    
    @abstractmethod
    def get_defect_class(self) -> type:
        """Return the defect class associated with this detector."""
        pass
    
    def _create_defect_instance(self, source_map, pcs: List[int]) -> Defect:
        """Create an instance of the defect class."""
        defect_class = self.get_defect_class()
        return defect_class(source_map, pcs)
    
    def _extract_detection_info(self, defect: Defect) -> DetectionResult:
        """Extract detection information from defect instance."""
        warnings = defect.get_warnings() if hasattr(defect, 'get_warnings') else []
        locations = [str(defect)] if str(defect) else []
        
        return DetectionResult(
            defect_name=self.name,
            is_defective=defect.is_defective(),
            warnings=warnings,
            locations=locations,
            description=self.description
        )