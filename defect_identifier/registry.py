"""Registry for managing defect detectors."""

from typing import Dict, List, Any, Optional
import logging
from defect_identifier.base_detector import DefectDetector, DetectionResult
from defect_identifier.detectors import (
    ViolationDetector,
    ReentrancyDetector,
    ProxyDetector, 
    UnlimitedMintingDetector,
    PublicBurnDetector
)

log = logging.getLogger(__name__)


class DefectRegistry:
    """Registry for managing and executing defect detectors."""
    
    def __init__(self):
        self._detectors: Dict[str, DefectDetector] = {}
        self._detection_results: Dict[str, DetectionResult] = {}
        self._register_default_detectors()
    
    def _register_default_detectors(self):
        """Register all default defect detectors."""
        default_detectors = [
            ViolationDetector(),
            ReentrancyDetector(), 
            ProxyDetector(),
            UnlimitedMintingDetector(),
            PublicBurnDetector()
        ]
        
        for detector in default_detectors:
            self.register_detector(detector)
    
    def register_detector(self, detector: DefectDetector):
        """
        Register a new defect detector.
        
        Args:
            detector: The detector instance to register
        """
        if not isinstance(detector, DefectDetector):
            raise TypeError("Detector must inherit from DefectDetector")
        
        self._detectors[detector.name] = detector
        log.debug(f"Registered detector: {detector.name}")
    
    def unregister_detector(self, name: str) -> bool:
        """
        Unregister a defect detector.
        
        Args:
            name: Name of the detector to unregister
            
        Returns:
            True if detector was removed, False if not found
        """
        if name in self._detectors:
            del self._detectors[name]
            log.debug(f"Unregistered detector: {name}")
            return True
        return False
    
    def get_detector(self, name: str) -> Optional[DefectDetector]:
        """Get a detector by name."""
        return self._detectors.get(name)
    
    def list_detectors(self) -> List[str]:
        """Get list of registered detector names."""
        return list(self._detectors.keys())
    
    def detect_all(self, source_map, problematic_pcs: Dict[str, List[int]]) -> Dict[str, DetectionResult]:
        """
        Run all registered detectors.
        
        Args:
            source_map: Source map for code location mapping
            problematic_pcs: Dictionary mapping defect types to problematic PCs
            
        Returns:
            Dictionary mapping detector names to detection results
        """
        results = {}
        
        # Mapping from detector names to PC keys
        pc_mapping = {
            "ERC721 Standard Violation": "violation_defect",
            "ERC721 Reentrancy": "reentrancy_defect", 
            "Risky Mutable Proxy": "proxy_defect",
            "Unlimited Minting": "unlimited_minting_defect",
            "Public Burn": "burn_defect"
        }
        
        for detector_name, detector in self._detectors.items():
            try:
                pc_key = pc_mapping.get(detector_name, detector_name.lower() + "_defect")
                pcs = problematic_pcs.get(pc_key, [])
                result = detector.detect(source_map, pcs)
                results[detector_name] = result
                log.debug(f"Completed detection for {detector_name}: {result.is_defective}")
            except Exception as e:
                log.error(f"Error running detector {detector_name}: {e}")
                # Create error result
                results[detector_name] = DetectionResult(
                    defect_name=detector_name,
                    is_defective=False,
                    warnings=[f"Detection failed: {str(e)}"],
                    locations=[],
                    severity="error"
                )
        
        self._detection_results = results
        return results
    
    def get_results(self) -> Dict[str, DetectionResult]:
        """Get the last detection results."""
        return self._detection_results.copy()
    
    def has_any_defects(self) -> bool:
        """Check if any defects were found in the last detection run."""
        return any(result.is_defective for result in self._detection_results.values())
    
    def get_defective_results(self) -> Dict[str, DetectionResult]:
        """Get only the results that found defects."""
        return {
            name: result 
            for name, result in self._detection_results.items() 
            if result.is_defective
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert results to dictionary for JSON serialization."""
        return {
            name: result.to_dict() 
            for name, result in self._detection_results.items()
        }