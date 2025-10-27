import httpx
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class FMCSAService:
    """Service for verifying carriers via FMCSA API"""
    
    def __init__(self, http_client: httpx.AsyncClient, api_key: str, base_url: str):
        self.http_client = http_client
        self.api_key = api_key
        self.base_url = base_url
    
    async def verify_carrier(self, mc_number: str) -> Dict:
        """
        Verify a carrier using their MC number
        
        Returns dict with:
        - eligible: bool (True if carrier can haul loads)
        - carrier_name: str
        - allowed_to_operate: str ("Y" or "N")
        - status_code: str ("A" = Active, "I" = Inactive)
        - out_of_service: str ("Y" = out of service, "N" = in service)
        - message: str
        """
        
        try:
            # FMCSA API endpoint
            url = f"{self.base_url}/carriers/docket-number/{mc_number}"
            params = {"webKey": self.api_key}
            
            logger.info(f"Calling FMCSA API for MC {mc_number}")
            
            response = await self.http_client.get(url, params=params)
            
            # Handle HTTP errors
            if response.status_code == 404:
                logger.warning(f"MC {mc_number} not found in FMCSA database")
                return self._not_found_response(mc_number)
            
            if response.status_code != 200:
                logger.error(f"FMCSA API error {response.status_code}")
                return self._error_response(response.status_code)
            
            # Parse response
            data = response.json()
            
            # Validate response structure
            if not data.get("content") or not isinstance(data["content"], list):
                logger.warning(f"Invalid response structure for MC {mc_number}")
                return self._not_found_response(mc_number)
            
            # Get carrier data (content is a list)
            carrier_data = data["content"][0]
            carrier = carrier_data.get("carrier", {})
            
            # Extract fields
            carrier_name = carrier.get("legalName", "Unknown")
            allowed_to_operate = carrier.get("allowedToOperate", "N")
            status_code = carrier.get("statusCode", "N/A")
            
            # Insurance check - bipdInsuranceOnFile is a DOLLAR AMOUNT
            insurance_amount_str = carrier.get("bipdInsuranceOnFile", "0")
            try:
                insurance_amount = int(insurance_amount_str)
            except (ValueError, TypeError):
                insurance_amount = 0
            
            # Insurance required amount
            insurance_required_str = carrier.get("bipdRequiredAmount", "0")
            try:
                insurance_required = int(insurance_required_str)
            except (ValueError, TypeError):
                insurance_required = 0
            
            # Check if insurance is adequate
            has_adequate_insurance = insurance_amount >= insurance_required and insurance_required > 0
            
            # Out of service indicators
            out_of_service_date = carrier.get("oosDate", "")
            has_oos_date = bool(out_of_service_date and out_of_service_date.strip())
            
            # Determine if carrier is OUT OF SERVICE
            out_of_service = "Y" if has_oos_date else "N"
            
            # ELIGIBILITY LOGIC:
            # Carrier is ELIGIBLE if:
            # 1. Allowed to operate = "Y"
            # 2. Status is Active ("A")
            # 3. NOT out of service
            # (Insurance check removed per requirements)
            
            eligible = (
                allowed_to_operate == "Y" and
                status_code == "A" and
                out_of_service == "N"
            )
            
            # Build message
            if eligible:
                message = "Carrier is eligible and authorized to operate"
            else:
                reasons = []
                if allowed_to_operate != "Y":
                    reasons.append("not authorized to operate")
                if status_code != "A":
                    reasons.append(f"status is {status_code} (not Active)")
                if out_of_service == "Y":
                    reasons.append("currently out of service")
                
                message = f"Carrier is not eligible: {', '.join(reasons)}"
            
            logger.info(
                f"MC {mc_number}: {carrier_name} - "
                f"Eligible={eligible}, Allowed={allowed_to_operate}, "
                f"Status={status_code}, OOS={out_of_service}"
            )
            
            # Return carrier information
            return {
                "eligible": eligible,
                "carrier_name": carrier_name,
                "mc_number": mc_number,
                "dot_number": str(carrier.get("dotNumber", "")),
                "allowed_to_operate": allowed_to_operate,
                "status_code": status_code,
                "status_description": "Active" if status_code == "A" else "Inactive" if status_code == "I" else "Unknown",
                "out_of_service": out_of_service,
                "insurance_on_file": insurance_amount,
                "insurance_required": insurance_required,
                "carrier_operation": carrier.get("carrierOperation", {}).get("carrierOperationDesc", ""),
                "city": carrier.get("phyCity", ""),
                "state": carrier.get("phyState", ""),
                "address": carrier.get("phyStreet", ""),
                "zip_code": carrier.get("phyZipcode", ""),
                "phone": carrier.get("telephone", ""),
                "message": message
            }
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling FMCSA API: {e}")
            return self._error_response(str(e))
        except Exception as e:
            logger.error(f"Unexpected error verifying carrier: {e}")
            logger.exception("Full traceback:")
            return self._error_response(str(e))
    
    def _not_found_response(self, mc_number: str) -> Dict:
        """Standard response for carrier not found"""
        return {
            "eligible": False,
            "carrier_name": "Unknown",
            "allowed_to_operate": "N",
            "status_code": "N/A",
            "out_of_service": "N/A",
            "insurance_on_file": 0,
            "insurance_required": 0,
            "carrier_operation": "",
            "city": "",
            "state": "",
            "dot_number": "",
            "message": f"Carrier MC {mc_number} not found in FMCSA database"
        }
    
    def _error_response(self, error: str) -> Dict:
        """Standard response for API errors"""
        return {
            "eligible": False,
            "carrier_name": "Unknown",
            "allowed_to_operate": "N",
            "status_code": "ERROR",
            "out_of_service": "N/A",
            "insurance_on_file": 0,
            "insurance_required": 0,
            "carrier_operation": "",
            "city": "",
            "state": "",
            "dot_number": "",
            "message": f"FMCSA API error: {error}"
        }