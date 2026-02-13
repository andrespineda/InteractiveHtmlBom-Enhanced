"""
Part Search Module for InteractiveHtmlBom
Provides search functionality for Digi-Key, Mouser, and JLCPCB
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
    description: str
    value: str
    footprint: str
    stock: int
    price: float
    url: str
    datasheet: str
    lcsc_part: str = ""  # JLCPCB LCSC part number


class JLCPCBClient:
    """Client for JLCPCB component search using JLCSearch API"""

    def __init__(self):
        self.jlcsearch_base = "https://jlcsearch.tscircuit.com"

    def search_components(
        self,
        search_term: str,
        package: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Search for components on JLCPCB using JLCSearch API"""
        try:
            params = {
                'search': search_term,
                'limit': limit,
                'full': 'true'
            }
            if package:
                params['package'] = package

            response = requests.get(
                f"{self.jlcsearch_base}/components/list.json",
                params=params,
                timeout=30
            )

            if response.status_code != 200:
                logger.warning(f"JLCSearch API error: {response.status_code}")
                return []

            data = response.json()
            return data.get('components', [])

        except Exception as e:
            logger.error(f"JLCSearch search error: {e}")
            return []

    def select_best_part(self, components: List[Dict]) -> Optional[Dict]:
        """Select best part from results based on stock and price"""
        if not components:
            return None

        # Filter for in-stock parts
        in_stock = []
        for comp in components:
            stock = 0
            if 'stock' in comp:
                try:
                    stock = int(comp['stock'])
                except (ValueError, TypeError):
                    pass
            elif 'stockQty' in comp:
                try:
                    stock = int(comp['stockQty'])
                except (ValueError, TypeError):
                    pass

            if stock > 0:
                comp['_stock'] = stock
                in_stock.append(comp)

        if not in_stock:
            return components[0]

        # Sort by stock (descending), then by price (ascending)
        def sort_key(comp):
            stock = comp.get('_stock', 0)
            price = 0.0
            if 'price' in comp:
                try:
                    price = float(str(comp['price']).replace(',', ''))
                except (ValueError, TypeError):
                    pass
            return (-stock, price)

        in_stock.sort(key=sort_key)
        return in_stock[0]


class PartSearcher:
    """Main class for part search across multiple suppliers"""

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize part searcher

        Args:
            config: Optional dictionary with API keys:
                {
                    'digikey_client_id': str,
                    'digikey_client_secret': str,
                    'mouser_api_key': str
                }
        """
        self.config = config or {}
        self.jlcpcb_client = JLCPCBClient()
        self.digikey_api_base = "https://api.digikey.com"
        self.mouser_api_base = "https://api.mouser.com/api/v1"

    def search_jlcpcb(
        self,
        value: str,
        footprint: Optional[str] = None,
        manufacturer: Optional[str] = None,
        mfg_part: Optional[str] = None
    ) -> List[PartSearchResult]:
        """
        Search for parts on JLCPCB

        Args:
            value: Component value (e.g., "100K", "1uF")
            footprint: Optional metric footprint (e.g., "0402", "0603")
            manufacturer: Optional manufacturer name
            mfg_part: Optional manufacturer part number

        Returns:
            List of PartSearchResult objects
        """
        results = []

        # First try by manufacturer part number if provided
        if mfg_part:
            search_term = mfg_part
            if manufacturer:
                search_term = f"{manufacturer} {mfg_part}"

            components = self.jlcpcb_client.search_components(
                search_term=search_term,
                limit=10
            )

            if components:
                best_match = self.jlcpcb_client.select_best_part(components)
                if best_match:
                    results.append(self._parse_jlcpcb_result(best_match, value, footprint))
                    return results

        # Then try by value and footprint
        if footprint:
            components = self.jlcpcb_client.search_components(
                search_term=value,
                package=footprint,
                limit=10
            )
        else:
            components = self.jlcpcb_client.search_components(
                search_term=value,
                limit=10
            )

        if components:
            # Return top 5 results
            for comp in components[:5]:
                results.append(self._parse_jlcpcb_result(comp, value, footprint))

        return results

    def search_digikey(
        self,
        value: str,
        footprint: Optional[str] = None,
        component_type: Optional[str] = None
    ) -> List[PartSearchResult]:
        """
        Search for parts on Digi-Key

        Args:
            value: Component value
            footprint: Optional footprint
            component_type: Optional component type (resistor, capacitor, etc.)

        Returns:
            List of PartSearchResult objects
        """
        if not self.config.get('digikey_client_id'):
            logger.warning("Digi-Key API keys not configured")
            return []

        results = []

        try:
            # Get access token
            token_response = requests.post(
                f"{self.digikey_api_base}/v1/oauth2/token",
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                data={
                    'client_id': self.config.get('digikey_client_id'),
                    'client_secret': self.config.get('digikey_client_secret'),
                    'grant_type': 'client_credentials'
                }
            )

            if token_response.status_code != 200:
                logger.error(f"Digi-Key token request failed: {token_response.text}")
                return []

            token = token_response.json().get('access_token')

            # Build search parameters
            search_term = f"{value} {footprint}" if footprint else value
            if component_type:
                search_term = f"{component_type} {value} {footprint}" if footprint else f"{component_type} {value}"

            # Search for parts
            search_response = requests.get(
                f"{self.digikey_api_base}/Products/v3/Search/Keyword",
                headers={
                    'Authorization': f'Bearer {token}',
                    'X-Digikey-Client-Id': self.config.get('digikey_client_id'),
                    'Content-Type': 'application/json'
                },
                params={
                    'Keyword': search_term,
                    'limit': 10
                }
            )

            if search_response.status_code != 200:
                logger.warning(f"Digi-Key search failed: {search_response.text}")
                return []

            search_data = search_response.json()

            if 'Products' in search_data:
                for product in search_data['Products'][:5]:
                    results.append(self._parse_digikey_result(product, value, footprint))

        except Exception as e:
            logger.error(f"Digi-Key search error: {e}")

        return results

    def search_mouser(
        self,
        value: str,
        footprint: Optional[str] = None,
        component_type: Optional[str] = None
    ) -> List[PartSearchResult]:
        """
        Search for parts on Mouser

        Args:
            value: Component value
            footprint: Optional footprint
            component_type: Optional component type

        Returns:
            List of PartSearchResult objects
        """
        if not self.config.get('mouser_api_key'):
            logger.warning("Mouser API key not configured")
            return []

        results = []

        try:
            search_term = f"{value} {footprint}" if footprint else value
            if component_type:
                search_term = f"{component_type} {value} {footprint}" if footprint else f"{component_type} {value}"

            search_response = requests.post(
                f"{self.mouser_api_base}/product/search",
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f"Bearer {self.config.get('mouser_api_key')}"
                },
                json={
                    'SearchByKeywordRequest': {
                        'keyword': search_term,
                        'records': 10,
                        'searchOptions': 'InStock'
                    }
                }
            )

            if search_response.status_code != 200:
                logger.warning(f"Mouser search failed: {search_response.text}")
                return []

            search_data = search_response.json()

            if 'SearchResults' in search_data and 'Parts' in search_data['SearchResults']:
                for part in search_data['SearchResults']['Parts'][:5]:
                    results.append(self._parse_mouser_result(part, value, footprint))

        except Exception as e:
            logger.error(f"Mouser search error: {e}")

        return results

    def search_all(
        self,
        value: str,
        footprint: Optional[str] = None,
        component_type: Optional[str] = None,
        manufacturer: Optional[str] = None,
        mfg_part: Optional[str] = None
    ) -> Dict[str, List[PartSearchResult]]:
        """
        Search for parts across all configured suppliers

        Returns:
            Dictionary with supplier names as keys and lists of results as values
        """
        results = {}

        # Search JLCPCB
        jlcpcb_results = self.search_jlcpcb(value, footprint, manufacturer, mfg_part)
        if jlcpcb_results:
            results['JLCPCB'] = jlcpcb_results

        # Search Digi-Key
        digikey_results = self.search_digikey(value, footprint, component_type)
        if digikey_results:
            results['Digi-Key'] = digikey_results

        # Search Mouser
        mouser_results = self.search_mouser(value, footprint, component_type)
        if mouser_results:
            results['Mouser'] = mouser_results

        return results

    def _parse_jlcpcb_result(self, comp: Dict, value: str, footprint: Optional[str]) -> PartSearchResult:
        """Parse JLCSearch API result into PartSearchResult"""
        lcsc_part = ""
        if 'lcsc' in comp:
            lcsc_part = f"C{comp['lcsc']}" if str(comp['lcsc']).isdigit() else str(comp['lcsc'])
        elif 'lcscCode' in comp:
            lcsc_part = comp['lcscCode']

        stock = 0
        if 'stock' in comp:
            try:
                stock = int(comp['stock'])
            except (ValueError, TypeError):
                pass
        elif 'stockQty' in comp:
            try:
                stock = int(comp['stockQty'])
            except (ValueError, TypeError):
                pass

        price = 0.0
        if 'price' in comp:
            try:
                price = float(str(comp['price']).replace(',', ''))
            except (ValueError, TypeError):
                pass

        mfr = comp.get('mfr', comp.get('manufacturer', comp.get('Manufacturer', '')))
        desc = comp.get('description', comp.get('Description', ''))
        pkg = comp.get('package', footprint or '')

        return PartSearchResult(
            supplier="JLCPCB",
            part_number=comp.get('mfrPartNo', ''),
            manufacturer=mfr,
            description=desc,
            value=value,
            footprint=pkg,
            stock=stock,
            price=price,
            url=f"https://jlcpcb.com/part/{lcsc_part}",
            datasheet='',
            lcsc_part=lcsc_part
        )

    def _parse_digikey_result(self, product: Dict, value: str, footprint: Optional[str]) -> PartSearchResult:
        """Parse Digi-Key API result into PartSearchResult"""
        stock = product.get('QuantityAvailable', 0)

        price = 0.0
        pricing = product.get('StandardPricing', [])
        if pricing:
            try:
                price = float(pricing[0].get('UnitPrice', 0.0))
            except (ValueError, KeyError):
                pass

        return PartSearchResult(
            supplier="Digi-Key",
            part_number=product.get('ManufacturerPartNumber', ''),
            manufacturer=product.get('Manufacturer', {}).get('Name', ''),
            description=product.get('DetailedDescription', ''),
            value=value,
            footprint=footprint or '',
            stock=stock,
            price=price,
            url=product.get('ProductUrl', ''),
            datasheet=product.get('DatasheetUrl', '')
        )

    def _parse_mouser_result(self, part: Dict, value: str, footprint: Optional[str]) -> PartSearchResult:
        """Parse Mouser API result into PartSearchResult"""
        availability = part.get('Availability', '0')
        stock = 0
        import re
        match = re.search(r'(\d+)', str(availability))
        if match:
            stock = int(match.group(1))

        price = 0.0
        price_breaks = part.get('PriceBreaks', [])
        if price_breaks:
            try:
                price = float(price_breaks[0].get('Price', 0.0).replace(',', ''))
            except (ValueError, KeyError):
                pass

        return PartSearchResult(
            supplier="Mouser",
            part_number=part.get('ManufacturerPartNumber', ''),
            manufacturer=part.get('Manufacturer', ''),
            description=part.get('Description', ''),
            value=value,
            footprint=footprint or '',
            stock=stock,
            price=price,
            url=part.get('ProductDetailUrl', ''),
            datasheet=part.get('DataSheetUrl', '')
        )


def get_part_search_html() -> str:
    """Return HTML/JavaScript for part search UI"""
    return '''
<div id="part-search-panel" style="display:none; position:fixed; top:20%; left:50%; transform:translate(-50%,0); z-index:9999; background:white; padding:20px; border-radius:8px; box-shadow:0 4px 20px rgba(0,0,0,0.3); max-width:800px; max-height:80vh; overflow-y:auto;">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px; border-bottom:1px solid #eee; padding-bottom:10px;">
        <h3 style="margin:0; color:#333;">Component Search</h3>
        <button onclick="closePartSearch()" style="background:#dc3545; color:white; border:none; padding:8px 15px; border-radius:4px; cursor:pointer;">✕</button>
    </div>

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
                    <label><input type="checkbox" id="check-digikey"> Digi-Key</label>
                    <label><input type="checkbox" id="check-mouser"> Mouser</label>
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
let partSearchCache = {};

function openPartSearch(value, footprint) {
    document.getElementById('part-search-panel').style.display = 'block';
    document.getElementById('part-search-overlay').style.display = 'block';

    if (value) document.getElementById('search-value').value = value;
    if (footprint) document.getElementById('search-footprint').value = footprint;
}

function closePartSearch() {
    document.getElementById('part-search-panel').style.display = 'none';
    document.getElementById('part-search-overlay').style.display = 'none';
}

function searchParts() {
    const value = document.getElementById('search-value').value.trim();
    const footprint = document.getElementById('search-footprint').value.trim();
    const type = document.getElementById('search-type').value;
    const useJLCPCB = document.getElementById('check-jlcpcb').checked;
    const useDigiKey = document.getElementById('check-digikey').checked;
    const useMouser = document.getElementById('check-mouser').checked;

    if (!value && !footprint) {
        alert('Please enter a value or footprint to search');
        return;
    }

    const cacheKey = `${value}-${footprint}-${type}-${useJLCPCB}-${useDigiKey}-${useMouser}`;

    if (partSearchCache[cacheKey]) {
        displaySearchResults(partSearchCache[cacheKey]);
        return;
    }

    document.getElementById('search-input-section').style.display = 'none';
    document.getElementById('search-loading').style.display = 'block';

    const searchPromises = [];
    const results = {};

    // JLCPCB search (uses free JLCSearch API)
    if (useJLCPCB) {
        searchPromises.push(
            fetch('https://jlcsearch.tscircuit.com/components/list.json?search=' + encodeURIComponent(value + ' ' + footprint) + '&limit=10&full=true')
                .then(r => r.json())
                .then(data => {
                    results['JLCPCB'] = (data.components || []).map(c => ({
                        supplier: 'JLCPCB',
                        part_number: c.mfrPartNo || '',
                        manufacturer: c.mfr || c.manufacturer || '',
                        description: c.description || '',
                        value: value,
                        footprint: c.package || footprint || '',
                        stock: parseInt(c.stock) || 0,
                        price: parseFloat(c.price) || 0,
                        url: 'https://jlcpcb.com/part/' + (c.lsc || c.lcscCode),
                        datasheet: '',
                        lcsc_part: (c.lsc ? 'C' + c.lsc : c.lcscCode) || ''
                    }));
                })
                .catch(e => console.error('JLCPCB search error:', e))
        );
    }

    // Digi-Key search (would require backend proxy for API keys)
    if (useDigiKey) {
        results['Digi-Key'] = [{
            supplier: 'Digi-Key',
            part_number: '',
            manufacturer: 'Note',
            description: 'Digi-Key API search requires server-side implementation. Please configure API keys in the plugin settings.',
            value: value,
            footprint: footprint || '',
            stock: 0,
            price: 0,
            url: 'https://www.digikey.com/en/products/filter?keywords=' + encodeURIComponent(value),
            datasheet: '',
            lcsc_part: ''
        }];
    }

    // Mouser search (would require backend proxy for API keys)
    if (useMouser) {
        results['Mouser'] = [{
            supplier: 'Mouser',
            part_number: '',
            manufacturer: 'Note',
            description: 'Mouser API search requires server-side implementation. Please configure API keys in the plugin settings.',
            value: value,
            footprint: footprint || '',
            stock: 0,
            price: 0,
            url: 'https://www.mouser.com/ProductSearch/?Keyword=' + encodeURIComponent(value),
            datasheet: '',
            lcsc_part: ''
        }];
    }

    Promise.all(searchPromises).then(() => {
        partSearchCache[cacheKey] = results;
        document.getElementById('search-loading').style.display = 'none';
        document.getElementById('search-input-section').style.display = 'block';
        displaySearchResults(results);
    }).catch(() => {
        document.getElementById('search-loading').style.display = 'none';
        document.getElementById('search-input-section').style.display = 'block';
    });
}

function displaySearchResults(results) {
    const container = document.getElementById('search-results');
    let html = '';

    for (const [supplier, parts] of Object.entries(results)) {
        if (!parts || parts.length === 0) continue;

        const supplierColors = {
            'JLCPCB': '#1a73e8',
            'Digi-Key': '#e74c3c',
            'Mouser': '#17a2b8'
        };
        const color = supplierColors[supplier] || '#666';

        html += '<div style="margin-bottom:20px;">';
        html += '<h4 style="margin:0 0 10px 0; color:' + color + '; border-bottom:2px solid ' + color + '; padding-bottom:5px;">' + supplier + '</h4>';

        for (const part of parts) {
            const stockColor = part.stock > 0 ? '#28a745' : '#dc3545';
            const stockText = part.stock > 0 ? part.stock + ' in stock' : 'Out of stock';

            html += '<div style="border:1px solid #eee; border-radius:6px; padding:12px; margin-bottom:10px; background:#fafafa;">';

            if (part.lcsc_part && supplier === 'JLCPCB') {
                html += '<div style="background:#e8f5e9; color:#333; padding:4px 8px; border-radius:4px; font-size:12px; margin-bottom:8px; display:inline-block;">LCSC: ' + part.lcsc_part + '</div>';
            }

            html += '<div style="display:grid; grid-template-columns: 2fr 1fr 1fr; gap:10px; margin-bottom:8px;">';
            html += '<div><strong>Part:</strong> ' + (part.part_number || 'N/A') + '</div>';
            html += '<div><strong>Mfg:</strong> ' + (part.manufacturer || 'N/A') + '</div>';
            html += '<div style="color:' + stockColor + ';">' + stockText + '</div>';
            html += '</div>';

            html += '<div style="color:#666; margin-bottom:8px;">' + (part.description || 'No description') + '</div>';

            html += '<div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">';
            html += '<div><strong>Price:</strong> $' + part.price.toFixed(4) + '</div>';
            html += '<div><strong>Footprint:</strong> ' + (part.footprint || 'N/A') + '</div>';
            html += '</div>';

            html += '<div style="margin-top:10px; text-align:right;">';
            html += '<a href="' + part.url + '" target="_blank" style="display:inline-block; background:' + color + '; color:white; padding:8px 20px; text-decoration:none; border-radius:4px;">View Part →</a>';
            if (part.datasheet) {
                html += ' <a href="' + part.datasheet + '" target="_blank" style="display:inline-block; background:#6c757d; color:white; padding:8px 20px; text-decoration:none; border-radius:4px; margin-left:10px;">Datasheet</a>';
            }
            html += '</div>';

            html += '</div>';
        }

        html += '</div>';
    }

    if (html === '') {
        html = '<div style="text-align:center; padding:30px; color:#666;">No results found. Try adjusting your search terms.</div>';
    }

    container.innerHTML = html;
}
</script>
<style>
#part-search-panel {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}
</style>
'''


def get_part_search_button_html() -> str:
    """Return HTML for the part search button that can be added to BOM"""
    return '''
<button onclick="openPartSearch()" style="background:#17a2b8; color:white; border:none; padding:8px 15px; border-radius:4px; cursor:pointer; margin-left:10px;">
    🔍 Search Parts
</button>
'''
