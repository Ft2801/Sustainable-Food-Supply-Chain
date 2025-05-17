import asyncio
import pytest
from off_chain.enforcement import (
    SafetyEnforcer,
    SafetyViolationError,
    GuaranteeResponseEnforcer,
    GuaranteeResponseError
)

# Initialize enforcers
safety_enforcer = SafetyEnforcer()
response_enforcer = GuaranteeResponseEnforcer()

# Example of using both enforcers together
@safety_enforcer.enforce_safety('product_validation')
@response_enforcer.enforce_response_time('quality_check')
async def validate_product_quality(
    temperature: float, humidity: float, quality_score: float):
    # Simulate some processing time
    await asyncio.sleep(1)
    return {
        'temperature': temperature,
        'humidity': humidity,
        'quality_score': quality_score,
        'validated': True
    }

# Test cases
@pytest.mark.asyncio
async def test_valid_product_parameters():
    try:
        result = await validate_product_quality(
            temperature=20.0,
            humidity=50.0,
            quality_score=0.8
        )
        assert result['validated'] is True
    except Exception as e:
        pytest.fail(f"Should not have raised an exception: {str(e)}")

@pytest.mark.asyncio
async def test_invalid_temperature():
    with pytest.raises(SafetyViolationError):
        await validate_product_quality(
            temperature=35.0,  # Outside safe range
            humidity=50.0,
            quality_score=0.8
        )

@pytest.mark.asyncio
async def test_slow_response():
    # Update timeout to a very small value to force a timeout
    response_enforcer.update_timeout_limit('quality_check', 0.1) 
    with pytest.raises(GuaranteeResponseError):
        await validate_product_quality(
            temperature=20.0,
            humidity=50.0,
            quality_score=0.8
        )
    # Reset timeout to original value
    response_enforcer.update_timeout_limit('quality_check', 4.0)

# Example of synchronous function with safety enforcement
@safety_enforcer.enforce_safety('product_validation')
def check_product_emissions(co2_emissions: float):
    return {
        'co2_emissions': co2_emissions,
        'compliant': co2_emissions <= safety_enforcer.safety_rules['max_co2_emissions']
    }

def test_valid_emissions():
    result = check_product_emissions(co2_emissions=500)
    assert result['compliant'] is True

def test_invalid_emissions():
    with pytest.raises(SafetyViolationError):
        check_product_emissions(co2_emissions=1500)  # Exceeds maximum allowed
