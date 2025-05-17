"""
A complex module demonstrating various Python features for testing summarization.

This module implements a risk calculation system with multiple components
and nested structures to test different levels of summarization.
"""

from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime

@dataclass
class RiskFactor:
    """Represents a risk factor with its weight and value."""
    name: str
    weight: float
    value: float
    category: str
    
    def calculate_impact(self) -> float:
        """Calculate the weighted impact of this risk factor."""
        return self.weight * self.value

class RiskCalculator:
    """Main class for calculating and aggregating risk scores.
    
    This class handles the complex logic of combining multiple risk factors
    and producing both detailed and summary risk assessments.
    """
    
    def __init__(self, factors: List[RiskFactor], threshold: float = 0.7):
        """Initialize with risk factors and threshold.
        
        Args:
            factors: List of risk factors to consider
            threshold: Risk threshold for high-risk classification
        """
        self.factors = factors
        self.threshold = threshold
        self._cache: Dict[str, float] = {}
    
    def calculate_total_risk(self) -> float:
        """Calculate the total risk score across all factors.
        
        The total risk is a weighted sum of all risk factors, normalized
        to a 0-1 scale.
        
        Returns:
            Float between 0 and 1 representing total risk
        """
        if not self.factors:
            return 0.0
            
        total_impact = sum(f.calculate_impact() for f in self.factors)
        total_weight = sum(f.weight for f in self.factors)
        
        return total_impact / total_weight if total_weight > 0 else 0.0
    
    def get_risk_breakdown(self) -> Dict[str, float]:
        """Get a breakdown of risk scores by category.
        
        Returns:
            Dictionary mapping categories to their risk scores
        """
        breakdown = {}
        for factor in self.factors:
            if factor.category not in breakdown:
                breakdown[factor.category] = 0.0
            breakdown[factor.category] += factor.calculate_impact()
        
        return breakdown
    
    def _validate_factors(self) -> List[str]:
        """Internal method to validate risk factors.
        
        Returns:
            List of validation error messages
        """
        errors = []
        for factor in self.factors:
            if factor.weight < 0 or factor.weight > 1:
                errors.append(f"Invalid weight for factor {factor.name}")
            if factor.value < 0:
                errors.append(f"Invalid value for factor {factor.name}")
        return errors

def create_risk_report(calculator: RiskCalculator) -> Dict[str, Union[float, Dict[str, float], str]]:
    """Create a comprehensive risk report.
    
    This function takes a RiskCalculator instance and produces a detailed
    report including total risk, breakdown, and timestamp.
    
    Args:
        calculator: RiskCalculator instance to generate report from
        
    Returns:
        Dictionary containing the full risk report
    """
    return {
        "timestamp": datetime.now().isoformat(),
        "total_risk": calculator.calculate_total_risk(),
        "breakdown": calculator.get_risk_breakdown(),
        "status": "high_risk" if calculator.calculate_total_risk() > calculator.threshold else "low_risk"
    }

# Example usage
if __name__ == "__main__":
    factors = [
        RiskFactor("market_volatility", 0.8, 0.6, "market"),
        RiskFactor("credit_default", 0.9, 0.3, "credit"),
        RiskFactor("operational_error", 0.5, 0.4, "operational")
    ]
    
    calculator = RiskCalculator(factors)
    report = create_risk_report(calculator)
    print(f"Total Risk: {report['total_risk']:.2f}")
    print(f"Status: {report['status']}")
    print("Breakdown:", report['breakdown']) 