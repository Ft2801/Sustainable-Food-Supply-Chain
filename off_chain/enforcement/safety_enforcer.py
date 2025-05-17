from typing import Any, Callable, Dict, Optional, Union
from functools import wraps
import logging
from datetime import datetime

class SafetyEnforcer:
    def __init__(self):
        self.safety_violations = []
        self.safety_rules = {
            'temperature_range': (-5, 30),  # Celsius
            'humidity_range': (30, 75),     # Percentage
            'max_transit_time': 72,         # Hours
            'min_quality_score': 0.7,       # Quality threshold
            'max_co2_emissions': 1000,      # kg CO2 equivalent
        }
        self.logger = logging.getLogger(__name__)

    def enforce_safety(self, operation_type: str = 'default') -> Callable:
        def decorator(function: Callable) -> Callable:
            @wraps(function)
            def wrapper(*args, **kwargs) -> Any:
                operation_context = {
                    'operation_type': operation_type,
                    'timestamp': datetime.now(),
                    'args': args,
                    'kwargs': kwargs
                }

                # Pre-execution safety checks
                self._check_preconditions(operation_context)

                try:
                    result = function(*args, **kwargs)
                    # Post-execution safety checks
                    self._check_postconditions(result, operation_context)
                    return result
                except Exception as e:
                    self.logger.error(
                        f"Safety violation in {function.__name__}: {str(e)}")
                    self.safety_violations.append({
                        'timestamp': datetime.now(),
                        'operation': function.__name__,
                        'error': str(e)
                    })
                    raise SafetyViolationError(
                        f'Safety violation in {function.__name__}: {str(e)}') from e

            return wrapper
        return decorator

    def _check_preconditions(self, context: Dict[str, Any]) -> None:
        """Verify safety conditions before operation execution"""
        kwargs = context['kwargs']
        
        if 'temperature' in kwargs:
            temp = kwargs['temperature']
            min_temp, max_temp = self.safety_rules['temperature_range']
            if not min_temp <= temp <= max_temp:
                raise SafetyViolationError(
                    f"Temperature {temp}°C is outside safe range [{min_temp}, {max_temp}]°C"
                )

        if 'humidity' in kwargs:
            humidity = kwargs['humidity']
            min_hum, max_hum = self.safety_rules['humidity_range']
            if not min_hum <= humidity <= max_hum:
                raise SafetyViolationError(
                    f"Humidity {humidity}% is outside safe range [{min_hum}, {max_hum}]%"
                )

        if 'quality_score' in kwargs:
            quality = kwargs['quality_score']
            if quality < self.safety_rules['min_quality_score']:
                raise SafetyViolationError(
                    f"Quality score {quality} is below minimum threshold {
                        self.safety_rules['min_quality_score']}"
                )

        if 'co2_emissions' in kwargs:
            emissions = kwargs['co2_emissions']
            if emissions > self.safety_rules['max_co2_emissions']:
                raise SafetyViolationError(
                    f"CO2 emissions {emissions} kg exceed maximum allowed {self.safety_rules['max_co2_emissions']} kg"
                )

    def _check_postconditions(self, result: Any, context: Dict[str, Any]) -> None:
        """Verify safety conditions after operation execution"""
        if isinstance(result, dict):
            if 'quality_score' in result and result['quality_score'] < self.safety_rules['min_quality_score']:
                raise SafetyViolationError(
                    f"Result quality score {result['quality_score']} below minimum threshold")
            if 'temperature' in result:
                min_temp, max_temp = self.safety_rules['temperature_range']
                if not min_temp <= result['temperature'] <= max_temp:
                    raise SafetyViolationError(
                        f"Result temperature outside safe range")

    def get_safety_violations(self) -> list:
        """Return list of all safety violations"""
        return self.safety_violations

    def update_safety_rule(self,
    rule_name: str, value: Union[tuple, float, int]) -> None:
        """Update a safety rule with new values"""
        if rule_name in self.safety_rules:
            self.safety_rules[rule_name] = value
            self.logger.info(f"Updated safety rule {rule_name} to {value}")
        else:
            raise ValueError(f"Unknown safety rule: {rule_name}")

class SafetyViolationError(Exception):
    pass
