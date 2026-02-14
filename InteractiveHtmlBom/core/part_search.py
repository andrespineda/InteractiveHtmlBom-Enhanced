"""
Part Search Module for InteractiveHtmlBom
Provides search functionality using BOM Parts Sourcing API server
"""

import json
import logging
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PartSearchResult:
    """Data class for part search result"""
    supplier: str
    part_number: str
    manufacturer: str
    manufacturer_part_number: str
    description: str
    value: str
    footprint: str
    stock: int
    price: float
    currency: str
    url: str
    datasheet: str
    lcsc_part: str = ""  # JLCPCB LCSC part number
    image: str = ""
    package: str = ""


class BOMPartsSourcingClient:
    """Client for BOM Parts Sourcing API server"""
    
    def __init__(self, api_base_url: str = "http://localhost:3000"):
        """
        Initialize client
        
        Args:
            api_base_url: Base URL of the BOM Parts Sourcing API server
        """
        self.api_base_url = api_base_url.rstrip('/')
    
    def check_config(self) -> Dict:
        """Check API server configuration status"""
        try:
            response = requests.get(f"{self.api_base_url}/api/config", timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Config check failed: {e}")
        return {}
    
    def search_parts(
        self,
        value: str,
        footprint: Optional[str] = None,
        component_type: Optional[str] = None,
        suppliers: Optional[List[str]] = None,
        limit: int = 10
    ) -> Dict[str, List[PartSearchResult]]:
        """
        Search for parts across all suppliers
        
        Args:
            value: Component value (e.g., "100K", "1uF")
            footprint: Optional footprint/package (e.g., "0402", "0603")
            component_type: Optional type (resistor, capacitor, etc.)
            suppliers: List of suppliers to search ["jlcpcb", "digikey", "mouser"]
            limit: Max results per supplier
            
        Returns:
            Dictionary with supplier names as keys and lists of PartSearchResult as values
        """
        if suppliers is None:
            suppliers = ["jlcpcb", "digikey", "mouser"]
        
        results = {}
        
        try:
            response = requests.post(
                f"{self.api_base_url}/api/parts-search",
                headers={"Content-Type": "application/json"},
                json={
                    "value": value,
                    "footprint": footprint or "",
                    "componentType": component_type or "",
                    "suppliers": suppliers,
                    "limit": limit
                },
                timeout=60  # Allow more time for multiple API calls
            )
            
            if response.status_code != 200:
                logger.error(f"Search failed: {response.status_code} - {response.text}")
                return results
            
            data = response.json()
            
            if not data.get("success"):
                logger.error(f"Search unsuccessful: {data}")
                return results
            
            # Parse results by supplier
            for supplier, parts in data.get("results", {}).items():
                results[supplier] = [
                    self._parse_result(part) for part in parts
                ]
            
            # Log configuration status
            configured = data.get("configured", {})
            for supplier, is_configured in configured.items():
                if not is_configured:
                    logger.warning(f"{supplier} API not configured on server")
            
        except Exception as e:
            logger.error(f"Search error: {e}")
        
        return results
    
    def _parse_result(self, data: Dict) -> PartSearchResult:
        """Parse API response into PartSearchResult"""
        return PartSearchResult(
            supplier=data.get("supplier", ""),
            part_number=data.get("partNumber", ""),
            manufacturer=data.get("manufacturer", ""),
            manufacturer_part_number=data.get("manufacturerPartNumber", ""),
            description=data.get("description", ""),
            value=data.get("value", ""),
            footprint=data.get("footprint", ""),
            stock=data.get("stock", 0),
            price=data.get("price", 0.0),
            currency=data.get("currency", "USD"),
            url=data.get("url", ""),
            datasheet=data.get("datasheet", ""),
            lcsc_part=data.get("lcscPart", ""),
            image=data.get("image", ""),
            package=data.get("package", "")
        )


# Legacy class names for backward compatibility
class JLCPCBClient:
    """Legacy client - now uses BOMPartsSourcingClient internally"""
    
    def __init__(self, api_base_url: str = "http://localhost:3000"):
        self.client = BOMPartsSourcingClient(api_base_url)
    
    def search_components(
        self,
        search_term: str,
        package: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Search for components on JLCPCB"""
        results = self.client.search_parts(
            value=search_term,
            footprint=package,
            suppliers=["jlcpcb"],
            limit=limit
        )
        
        # Convert to legacy format
        components = []
        for part in results.get("JLCPCB", []):
            components.append({
                "mfrPartNo": part.manufacturer_part_number,
                "mfr": part.manufacturer,
                "description": part.description,
                "package": part.package or part.footprint,
                "stock": str(part.stock),
                "price": str(part.price),
                "lcsc": part.lcsc_part.replace("C", "") if part.lcsc_part else "",
                "lcscCode": part.lcsc_part
            })
        
        return components
    
    def select_best_part(self, components: List[Dict]) -> Optional[Dict]:
        """Select best part from results based on stock and price"""
        if not components:
            return None
        
        # Sort by stock (descending), then by price (ascending)
        def sort_key(comp):
            stock = int(comp.get("stock", 0))
            price = float(comp.get("price", 0))
            return (-stock, price)
        
        sorted_components = sorted(components, key=sort_key)
        return sorted_components[0]


class PartSearcher:
    """Main class for part search - uses BOM Parts Sourcing API"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize part searcher
        
        Args:
            config: Dictionary with configuration:
                {
                    'api_base_url': str,  # URL of BOM Parts Sourcing API
                    'digikey_client_id': str,  # Legacy - ignored
                    'digikey_client_secret': str,  # Legacy - ignored
                    'mouser_api_key': str  # Legacy - ignored
                }
        """
        self.config = config or {}
        api_url = self.config.get("api_base_url", "http://localhost:3000")
        self.client = BOMPartsSourcingClient(api_url)
        self.jlcpcb_client = JLCPCBClient(api_url)
        
        # Legacy attributes
        self.digikey_api_base = "https://api.digikey.com"
        self.mouser_api_base = "https://api.mouser.com/api/v1"
    
    def search_jlcpcb(
        self,
        value: str,
        footprint: Optional[str] = None,
        manufacturer: Optional[str] = None,
        mfg_part: Optional[str] = None
    ) -> List[PartSearchResult]:
        """Search for parts on JLCPCB"""
        search_term = mfg_part if mfg_part else value
        if manufacturer and mfg_part:
            search_term = f"{manufacturer} {mfg_part}"
        
        results = self.client.search_parts(
            value=search_term,
            footprint=footprint,
            suppliers=["jlcpcb"],
            limit=10
        )
        
        return results.get("JLCPCB", [])
    
    def search_digikey(
        self,
        value: str,
        footprint: Optional[str] = None,
        component_type: Optional[str] = None
    ) -> List[PartSearchResult]:
        """Search for parts on Digi-Key"""
        results = self.client.search_parts(
            value=value,
            footprint=footprint,
            component_type=component_type,
            suppliers=["digikey"],
            limit=10
        )
        
        return results.get("Digi-Key", [])
    
    def search_mouser(
        self,
        value: str,
        footprint: Optional[str] = None,
        component_type: Optional[str] = None
    ) -> List[PartSearchResult]:
        """Search for parts on Mouser"""
        results = self.client.search_parts(
            value=value,
            footprint=footprint,
            component_type=component_type,
            suppliers=["mouser"],
            limit=10
        )
        
        return results.get("Mouser", [])
    
    def search_all(
        self,
        value: str,
        footprint: Optional[str] = None,
        component_type: Optional[str] = None,
        manufacturer: Optional[str] = None,
        mfg_part: Optional[str] = None
    ) -> Dict[str, List[PartSearchResult]]:
        """Search for parts across all configured suppliers"""
        
        # Build search term
        search_term = value
        if mfg_part:
            search_term = mfg_part
            if manufacturer:
                search_term = f"{manufacturer} {mfg_part}"
        
        return self.client.search_parts(
            value=search_term,
            footprint=footprint,
            component_type=component_type,
            suppliers=["jlcpcb", "digikey", "mouser"],
            limit=10
        )


def get_part_search_html(api_base_url: str = "http://localhost:3000") -> str:
    """
    Return HTML/JavaScript for part search UI
    
    Args:
        api_base_url: Base URL of the BOM Parts Sourcing API server
    """
    return f'''
<div id="part-search-panel" style="display:none; position:fixed; top:20%; left:50%; transform:translate(-50%,0); z-index:9999; background:white; padding:20px; border-radius:8px; box-shadow:0 4px 20px rgba(0,0,0,0.3); max-width:800px; max-height:80vh; overflow-y:auto;">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px; border-bottom:1px solid #eee; padding-bottom:10px;">
        <h3 style="margin:0; color:#333;">Component Search</h3>
        <button onclick="closePartSearch()" style="background:#dc3545; color:white; border:none; padding:8px 15px; border-radius:4px; cursor:pointer;">✕</button>
    </div>

    <div id="search-config-status" style="margin-bottom:15px; padding:10px; background:#f8f9fa; border-radius:4px; font-size:12px;"></div>

    <div id="search-input-section">
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-bottom:15px;">
            <div>
                <label style="display:block; margin-bottom:5px; font-weight:bold; color:#555;">Value</label>
                <input type="text" id="search-value" placeholder="e.g., 100K, 1uF" style="width:100%; padding:8px; border:1px solid #ddd; border-radius:4px;">
            </div>
            <div>
                <label style="display:block; margin-bottom:5px; font-weight:bold; color:#555;">Footprint</label>
                <input type="text" id="search-footprint" placeholder="e.g., 0402, 0603" style="width:100%; padding:8px; border:1px solid #ddd; border-radius:4px;">
            </div>
        </div>

        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-bottom:15px;">
            <div>
                <label style="display:block; margin-bottom:5px; font-weight:bold; color:#555;">Component Type</label>
                <select id="search-type" style="width:100%; padding:8px; border:1px solid #ddd; border-radius:4px;">
                    <option value="">All Types</option>
                    <option value="resistor">Resistor</option>
                    <option value="capacitor">Capacitor</option>
                    <option value="inductor">Inductor</option>
                    <option value="diode">Diode</option>
                    <option value="led">LED</option>
                    <option value="transistor">Transistor</option>
                    <option value="ic">IC</option>
                    <option value="oscillator">Oscillator</option>
                    <option value="connector">Connector</option>
                </select>
            </div>
            <div>
                <label style="display:block; margin-bottom:5px; font-weight:bold; color:#555;">Suppliers</label>
                <div style="display:flex; gap:10px; padding-top:8px;">
                    <label><input type="checkbox" id="check-jlcpcb" checked> JLCPCB</label>
                    <label><input type="checkbox" id="check-digikey" checked> Digi-Key</label>
                    <label><input type="checkbox" id="check-mouser" checked> Mouser</label>
                </div>
            </div>
        </div>

        <button onclick="searchParts()" style="background:#28a745; color:white; border:none; padding:10px 25px; border-radius:4px; cursor:pointer; font-weight:bold; width:100%;">🔍 Search Parts</button>
    </div>

    <div id="search-loading" style="display:none; text-align:center; padding:20px;">
        <div style="color:#666; font-style:italic;">Searching suppliers...</div>
        <div style="margin-top:10px; color:#999;">This may take a moment</div>
    </div>

    <div id="search-results"></div>
</div>

<div id="part-search-overlay" style="display:none; position:fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.5); z-index:9998;" onclick="closePartSearch()"></div>

<script>
const BOM_API_URL = "{api_base_url}";
let partSearchCache = {{}};
let configStatus = {{}};

// Check API configuration on load
fetch(BOM_API_URL + '/api/config')
    .then(r => r.json())
    .then(data => {{
        configStatus = data.suppliers || {{}};
        updateConfigStatus();
    }})
    .catch(e => console.error('Config check failed:', e));

function updateConfigStatus() {{
    const container = document.getElementById('search-config-status');
    let html = '<strong>API Status:</strong> ';
    
    const suppliers = [
        {{key: 'jlcpcb', name: 'JLCPCB'}},
        {{key: 'digikey', name: 'Digi-Key'}},
        {{key: 'mouser', name: 'Mouser'}}
    ];
    
    for (const s of suppliers) {{
        const isConfigured = configStatus[s.key]?.configured;
        const color = isConfigured ? '#28a745' : '#dc3545';
        const symbol = isConfigured ? '✓' : '✗';
        html += `<span style="margin-right:10px; color:${{color}}">${{symbol}} ${{s.name}}</span>`;
    }}
    
    container.innerHTML = html;
}}

function openPartSearch(value, footprint) {{
    document.getElementById('part-search-panel').style.display = 'block';
    document.getElementById('part-search-overlay').style.display = 'block';

    if (value) document.getElementById('search-value').value = value;
    if (footprint) document.getElementById('search-footprint').value = footprint;
}}

function closePartSearch() {{
    document.getElementById('part-search-panel').style.display = 'none';
    document.getElementById('part-search-overlay').style.display = 'none';
}}

function searchParts() {{
    const value = document.getElementById('search-value').value.trim();
    const footprint = document.getElementById('search-footprint').value.trim();
    const type = document.getElementById('search-type').value;
    const useJLCPCB = document.getElementById('check-jlcpcb').checked;
    const useDigiKey = document.getElementById('check-digikey').checked;
    const useMouser = document.getElementById('check-mouser').checked;

    if (!value && !footprint) {{
        alert('Please enter a value or footprint to search');
        return;
    }}

    const cacheKey = `${{value}}-${{footprint}}-${{type}}-${{useJLCPCB}}-${{useDigiKey}}-${{useMouser}}`;

    if (partSearchCache[cacheKey]) {{
        displaySearchResults(partSearchCache[cacheKey]);
        return;
    }}

    document.getElementById('search-input-section').style.display = 'none';
    document.getElementById('search-loading').style.display = 'block';

    const suppliers = [];
    if (useJLCPCB) suppliers.push('jlcpcb');
    if (useDigiKey) suppliers.push('digikey');
    if (useMouser) suppliers.push('mouser');

    // Call BOM Parts Sourcing API
    fetch(BOM_API_URL + '/api/parts-search', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
            value: value,
            footprint: footprint,
            componentType: type,
            suppliers: suppliers,
            limit: 10
        }})
    }})
    .then(response => response.json())
    .then(data => {{
        document.getElementById('search-loading').style.display = 'none';
        document.getElementById('search-input-section').style.display = 'block';
        
        if (data.success) {{
            const results = {{}};
            
            // Map API response to display format
            for (const [supplier, parts] of Object.entries(data.results || {{}})) {{
                results[supplier] = parts.map(p => ({{
                    supplier: p.supplier,
                    part_number: p.partNumber,
                    manufacturer: p.manufacturer,
                    manufacturer_part_number: p.manufacturerPartNumber,
                    description: p.description,
                    value: p.value,
                    footprint: p.footprint || p.package,
                    stock: p.stock,
                    price: p.price,
                    currency: p.currency,
                    url: p.url,
                    datasheet: p.datasheet,
                    lcsc_part: p.lcscPart,
                    image: p.image,
                    package: p.package
                }}));
            }}
            
            partSearchCache[cacheKey] = results;
            displaySearchResults(results);
            
            // Update config status
            if (data.configured) {{
                const newConfig = {{}};
                for (const [k, v] of Object.entries(data.configured)) {{
                    newConfig[k] = {{ configured: v }};
                }}
                configStatus = newConfig;
                updateConfigStatus();
            }}
        }} else {{
            document.getElementById('search-results').innerHTML = 
                '<div style="text-align:center; padding:30px; color:#dc3545;">Search failed: ' + 
                (data.error || 'Unknown error') + '</div>';
        }}
    }})
    .catch(error => {{
        document.getElementById('search-loading').style.display = 'none';
        document.getElementById('search-input-section').style.display = 'block';
        document.getElementById('search-results').innerHTML = 
            '<div style="text-align:center; padding:30px; color:#dc3545;">Search error: ' + 
            error.message + '<br><br>Make sure the BOM Parts Sourcing API is running at ' + BOM_API_URL + '</div>';
    }});
}}

function displaySearchResults(results) {{
    const container = document.getElementById('search-results');
    let html = '';

    for (const [supplier, parts] of Object.entries(results)) {{
        if (!parts || parts.length === 0) continue;

        const supplierColors = {{
            'JLCPCB': '#1a73e8',
            'Digi-Key': '#e74c3c',
            'Mouser': '#17a2b8'
        }};
        const color = supplierColors[supplier] || '#666';

        html += '<div style="margin-bottom:20px;">';
        html += '<h4 style="margin:0 0 10px 0; color:' + color + '; border-bottom:2px solid ' + color + '; padding-bottom:5px;">' + supplier + ' <span style="font-size:12px; color:#666;">(' + parts.length + ' results)</span></h4>';

        for (const part of parts) {{
            const stockColor = part.stock > 0 ? '#28a745' : '#dc3545';
            const stockText = part.stock > 0 ? part.stock.toLocaleString() + ' in stock' : 'Out of stock';

            html += '<div style="border:1px solid #eee; border-radius:6px; padding:12px; margin-bottom:10px; background:#fafafa;">';

            if (part.lcsc_part && supplier === 'JLCPCB') {{
                html += '<div style="background:#e8f5e9; color:#333; padding:4px 8px; border-radius:4px; font-size:12px; margin-bottom:8px; display:inline-block;">LCSC: ' + part.lcsc_part + '</div>';
            }}

            html += '<div style="display:grid; grid-template-columns: 2fr 1fr 1fr; gap:10px; margin-bottom:8px;">';
            html += '<div><strong>Part:</strong> ' + (part.manufacturer_part_number || part.part_number || 'N/A') + '</div>';
            html += '<div><strong>Mfg:</strong> ' + (part.manufacturer || 'N/A') + '</div>';
            html += '<div style="color:' + stockColor + ';">' + stockText + '</div>';
            html += '</div>';

            html += '<div style="color:#666; margin-bottom:8px;">' + (part.description || 'No description') + '</div>';

            html += '<div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">';
            html += '<div><strong>Price:</strong> $' + part.price.toFixed(4) + '</div>';
            html += '<div><strong>Footprint:</strong> ' + (part.package || part.footprint || 'N/A') + '</div>';
            html += '</div>';

            html += '<div style="margin-top:10px; text-align:right;">';
            html += '<a href="' + part.url + '" target="_blank" style="display:inline-block; background:' + color + '; color:white; padding:8px 20px; text-decoration:none; border-radius:4px;">View Part →</a>';
            if (part.datasheet) {{
                html += ' <a href="' + part.datasheet + '" target="_blank" style="display:inline-block; background:#6c757d; color:white; padding:8px 20px; text-decoration:none; border-radius:4px; margin-left:10px;">Datasheet</a>';
            }}
            html += '</div>';

            html += '</div>';
        }}

        html += '</div>';
    }}

    if (html === '') {{
        html = '<div style="text-align:center; padding:30px; color:#666;">No results found. Try adjusting your search terms.</div>';
    }}

    container.innerHTML = html;
}}
</script>
<style>
#part-search-panel {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}}
</style>
'''


def get_part_search_button_html() -> str:
    """Return HTML for the part search button that can be added to BOM"""
    return '''
<button onclick="openPartSearch()" style="background:#17a2b8; color:white; border:none; padding:8px 15px; border-radius:4px; cursor:pointer; margin-left:10px;">
    🔍 Search Parts
</button>
'''
