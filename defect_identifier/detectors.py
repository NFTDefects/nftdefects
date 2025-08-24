"""Concrete defect detector implementations."""

from typing import List
from defect_identifier.base_detector import DefectDetector, DetectionResult
from defect_identifier.defect import (
    ViolationDefect,
    ReentrancyDefect, 
    RiskyProxyDefect,
    UnlimitedMintingDefect,
    PublicBurnDefect
)


class ViolationDetector(DefectDetector):
    """Detector for ERC721 standard violations."""
    
    def __init__(self):
        super().__init__(
            name="ERC721 Standard Violation",
            description="Detects violations of ERC721 standard requirements"
        )
    
    def detect(self, source_map, problematic_pcs: List[int]) -> DetectionResult:
        defect = self._create_defect_instance(source_map, problematic_pcs)
        return self._extract_detection_info(defect)
    
    def get_defect_class(self) -> type:
        return ViolationDefect


class ReentrancyDetector(DefectDetector):
    """Detector for ERC721 reentrancy vulnerabilities."""
    
    def __init__(self):
        super().__init__(
            name="ERC721 Reentrancy",
            description="Detects reentrancy vulnerabilities in ERC721 contracts"
        )
    
    def detect(self, source_map, problematic_pcs: List[int]) -> DetectionResult:
        defect = self._create_defect_instance(source_map, problematic_pcs)
        return self._extract_detection_info(defect)
    
    def get_defect_class(self) -> type:
        return ReentrancyDefect


class ProxyDetector(DefectDetector):
    """Detector for risky mutable proxy patterns."""
    
    def __init__(self):
        super().__init__(
            name="Risky Mutable Proxy",
            description="Detects risky mutable proxy implementation patterns"
        )
    
    def detect(self, source_map, problematic_pcs: List[int]) -> DetectionResult:
        defect = self._create_defect_instance(source_map, problematic_pcs)
        return self._extract_detection_info(defect)
    
    def get_defect_class(self) -> type:
        return RiskyProxyDefect


class UnlimitedMintingDetector(DefectDetector):
    """Detector for unlimited minting vulnerabilities."""
    
    def __init__(self):
        super().__init__(
            name="Unlimited Minting",
            description="Detects unlimited minting vulnerabilities in NFT contracts"
        )
    
    def detect(self, source_map, problematic_pcs: List[int]) -> DetectionResult:
        defect = self._create_defect_instance(source_map, problematic_pcs)
        return self._extract_detection_info(defect)
    
    def get_defect_class(self) -> type:
        return UnlimitedMintingDefect


class PublicBurnDetector(DefectDetector):
    """Detector for public burn vulnerabilities."""
    
    def __init__(self):
        super().__init__(
            name="Public Burn",
            description="Detects unauthorized public burn functionalities"
        )
    
    def detect(self, source_map, problematic_pcs: List[int]) -> DetectionResult:
        defect = self._create_defect_instance(source_map, problematic_pcs)
        return self._extract_detection_info(defect)
    
    def get_defect_class(self) -> type:
        return PublicBurnDefect