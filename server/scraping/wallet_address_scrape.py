from goplus.address import Address
from typing import Dict, Any, Tuple
import json

async def scrape_wallet(address: str) -> Tuple[Dict[str, Any], str]:
    """
    Fetches and structures address security data from GoPlus API.
    
    Args:
        address: Ethereum address to analyze (e.g. "0x123...abc")
    
    Returns:
        tuple: (original_data_dict, formatted_string_response)
    """
    try:
        # Fetch raw response
        raw_response = Address(access_token=None).address_security(address=address)
        
        # Convert nested objects to plain dictionaries
        def clean_data(obj):
            if isinstance(obj, dict):
                return {k: clean_data(v) for k, v in obj.items()}
            elif hasattr(obj, '__dict__'):
                return clean_data(obj.__dict__)
            elif isinstance(obj, list):
                return [clean_data(i) for i in obj]
            return obj
        
        cleaned_data = clean_data(raw_response)
        
        # Create beautiful string representation with all keys
        def format_data(data, indent=0):
            lines = []
            indent_str = " " * indent
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (dict, list)):
                        lines.append(f"{indent_str}{key}:")
                        lines.append(format_data(value, indent + 2))
                    else:
                        lines.append(f"{indent_str}{key}: {value}")
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    lines.append(f"{indent_str}[{i}]:")
                    lines.append(format_data(item, indent + 2))
            else:
                lines.append(f"{indent_str}{data}")
            return "\n".join(lines)
        
        header = f"🔍 Security Report for {address}\n" + "=" * 50 + "\n"
        formatted_string = header + format_data(cleaned_data)
        
        return cleaned_data, formatted_string
    
    except Exception as e:
        error_msg = f"❌ Error analyzing address {address}:\n{str(e)}"
        return {}, error_msg

# # Example usage
# if __name__ == "__main__":
#     import asyncio
    
#     async def main():
#         address = "0x40929f552553b3efd811dc3d6e10b7abe5a5db78"
#         data, report = await scrape_wallet(address)
#         print(report)
    
#     asyncio.run(main())