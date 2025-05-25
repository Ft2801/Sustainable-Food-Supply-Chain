from typing import Any, Callable, Optional, List, Dict
from functools import wraps
import asyncio
import time
import logging
from datetime import datetime
from dataclasses import dataclass, field

# Definiamo un dataclass per contenere le informazioni sulla violazione
@dataclass
class ViolationInfo:
    function_name: str
    operation_type: str
    execution_time: int
    timeout_limit: int
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

class GuaranteeResponseError(Exception):
    """Custom exception for response time violations."""
    pass

class GuaranteeResponseEnforcer:
    def __init__(self):
        self.response_violations: List[ViolationInfo] = [] # Tipo specificato
        self.timeout_limits: Dict[str, int] = {      # Tipo specificato
            'default': 5.0,                 # seconds
            'blockchain_operation': 30.0,   # longer timeout for blockchain operations
            'database_query': 3.0,         # database operations
            'product_validation': 2.0,     # product validation checks
            'quality_check': 4.0,          # quality control operations
            'sensor_data': 2.0             # IoT sensor data processing
        }
        self.logger = logging.getLogger(__name__)

    def enforce_response_time(self, operation_type: str = 'default') -> Callable:
        def decorator(function: Callable) -> Callable:
            @wraps(function)
            async def async_wrapper(*args, **kwargs) -> Any:
                # C0301: Line too long - spezzata l'assegnazione di timeout
                default_timeout = self.timeout_limits['default']
                timeout = self.timeout_limits.get(operation_type, default_timeout)
                start_time = time.time()

                try:
                    # La chiamata ad asyncio.wait_for è mantenuta su una riga se possibile
                    result = await asyncio.wait_for(
                        function(*args, **kwargs),
                        timeout=timeout
                    )
                    execution_time = time.time() - start_time

                    self._log_execution_metrics(
                        function.__name__,
                        operation_type,
                        execution_time,
                        timeout
                    )

                    return result

                # W0707: raise-missing-from
                except asyncio.TimeoutError as te:
                    execution_time = time.time() - start_time
                    # R0913, R0917: Usare ViolationInfo
                    error_msg = "Async operation timed out via asyncio.wait_for"
                    violation_details = ViolationInfo(
                        function_name=function.__name__,
                        operation_type=operation_type,
                        execution_time=execution_time,
                        timeout_limit=timeout,
                        error_message=error_msg
                    )
                    self._record_violation(violation_details)
                    # C0301: Line too long - spezzata la stringa dell'eccezione
                    error_display_msg = (
                        f"Operation {function.__name__} timed out"
                        f" after {timeout:.2f} seconds"
                    )
                    raise GuaranteeResponseError(error_display_msg) from te

            @wraps(function)
            def sync_wrapper(*args, **kwargs) -> Any:
                # C0301: Line too long - spezzata l'assegnazione di timeout
                default_timeout = self.timeout_limits['default']
                timeout = self.timeout_limits.get(operation_type, default_timeout)
                start_time = time.time()

                try:
                    result = function(*args, **kwargs)
                    execution_time = time.time() - start_time

                    if execution_time > timeout:
                        # R0913, R0917: Usare ViolationInfo
                        error_msg = "Sync operation exceeded timeout"
                        violation_details = ViolationInfo(
                            function_name=function.__name__,
                            operation_type=operation_type,
                            execution_time=execution_time,
                            timeout_limit=timeout,
                            error_message=error_msg
                        )
                        self._record_violation(violation_details)
                        # C0301: Line too long - spezzata la stringa dell'eccezione
                        error_display_msg = (
                            f"Operation {function.__name__} exceeded timeout"
                            f" of {timeout:.2f} seconds"
                        )
                        raise GuaranteeResponseError(error_display_msg)

                    self._log_execution_metrics(
                        function.__name__,
                        operation_type,
                        execution_time,
                        timeout
                    )

                    return result
                # C0103: invalid-name (rinominato 'e' in 'exc')
                except Exception as exc:
                    execution_time = time.time() - start_time
                    # R0913, R0917: Usare ViolationInfo
                    violation_details = ViolationInfo(
                        function_name=function.__name__,
                        operation_type=operation_type,
                        execution_time=execution_time,
                        timeout_limit=timeout,
                        error_message=str(exc)
                    )
                    self._record_violation(violation_details)
                    raise # Rilancia l'eccezione originale

            return async_wrapper if asyncio.iscoroutinefunction(function) else sync_wrapper
        return decorator

    # R0913, R0917: Modificato per accettare un oggetto ViolationInfo
    def _record_violation(self, info: ViolationInfo) -> None:
        """Record a response time violation"""
        self.response_violations.append(info)

        # W1203: Use lazy % formatting in logging functions
        # C0301: Line too long - spezzata la stringa di formato del log
        log_format_string = (
            "Violation in %s (type: %s): exec_time %.2fs, limit %.2fs."
        )
        log_args = [info.function_name, info.operation_type,
                    info.execution_time, info.timeout_limit]

        if info.error_message:
            log_format_string += " Error: %s"
            log_args.append(info.error_message)

        self.logger.warning(log_format_string, *log_args)


    def _log_execution_metrics(self,
                             function_name: str,
                             operation_type: str,
                             execution_time: int,
                             timeout: int) -> None:
        """Log execution metrics for monitoring"""
        # W1203: Use lazy % formatting in logging functions
        # C0301: Line too long - spezzata la stringa di formato del log
        log_format_string = (
            "Operation metrics - Function: %s, Type: %s, "
            "Time: %.2fs, Limit: %.2fs"
        )
        self.logger.info(
            log_format_string,
            function_name,
            operation_type,
            execution_time,
            timeout
        )

    def get_response_violations(self) -> List[ViolationInfo]: 
        """Return list of all response time violations"""
        return self.response_violations

    def update_timeout_limit(self, operation_type: str, timeout: int) -> None:
        """Update timeout limit for an operation type"""
        if timeout <= 0:
            raise ValueError("Timeout must be positive")
        self.timeout_limits[operation_type] = timeout
        # W1203: Use lazy % formatting in logging functions
        self.logger.info(
            "Updated timeout limit for %s to %.2fs",
            operation_type,
            timeout
        )

    def get_timeout_limit(self, operation_type: str) -> int:
        """Get timeout limit for an operation type"""
        default_timeout = self.timeout_limits['default']
        return self.timeout_limits.get(operation_type, default_timeout)
