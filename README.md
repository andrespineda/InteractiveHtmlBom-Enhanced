# InteractiveHtmlBom-Enhanced

Enhanced version of InteractiveHtmlBom with integrated Digi-Key, Mouser, and JLCPCB part search functionality.

![icon](https://i.imgur.com/js4kDOn.png)

This is a fork of the excellent [InteractiveHtmlBom](https://github.com/openscopeproject/InteractiveHtmlBom) plugin for KiCad, with added **component parts search functionality** that allows you to quickly find and purchase components from major suppliers directly from the generated BOM HTML page.

## ⚡ What's New - Full API Integration!

### 🔍 Component Parts Search with Real-Time Data

The enhanced version now connects to the **BOM Parts Sourcing API** for full integration with all three major suppliers:

- **JLCPCB** - Full API integration with real-time stock, pricing, and LCSC part numbers
- **Digi-Key** - Full API integration with stock, pricing, and datasheets
- **Mouser** - Full API integration with stock, pricing, and datasheets

#### Key Features:

- **Real-time data**: Stock levels, pricing, and specifications from all suppliers
- **JLCPCB Priority**: JLCPCB results are shown first (China-based, no import needed for PCBA)
- **Pre-filled search**: Clicking the "🔍 Parts" button automatically pre-fills the component value and footprint from the selected BOM row
- **Multi-supplier search**: Search all suppliers simultaneously with one click
- **Smart caching**: Search results are cached to avoid repeated API calls
- **Stock awareness**: See at a glance which parts are in stock with color coding
- **One-click purchase**: Direct links to purchase pages for each supplier
- **Datasheet links**: Direct links to component datasheets when available

## Original Features

All original InteractiveHtmlBom features are preserved:

- Visual BOM with PCB board rendering
- Component highlighting and grouping
- Multiple view layouts (Front/Back/Split)
- Netlist highlighting
- Fab layer and silkscreen toggles
- BOM export to CSV/TXT
- Board image export
- Dark mode support
- And all other original features...

## Installation

### Prerequisites

1. **BOM Parts Sourcing API** - This plugin requires the BOM Parts Sourcing API server to be running:
   ```bash
   git clone https://github.com/andrespineda/bom-parts-sourcing.git
   cd bom-parts-sourcing
   bun install
   bun run dev
   ```
   The API server runs on `http://localhost:3000` by default.

2. **API Keys** (optional but recommended):
   - **Digi-Key**: Get credentials at [developer.digikey.com](https://developer.digikey.com/)
   - **Mouser**: Get API key at [mouser.com/api](https://www.mouser.com/api/)
   - **JLCPCB**: No API key needed (uses free JLCSearch API)

### Method 1: Plugin Directory (Recommended for KiCad 7+)

1. Clone or download this repository:
   ```bash
   git clone https://github.com/andrespineda/InteractiveHtmlBom-Enhanced.git
   ```

2. Open KiCad and go to **Tools → External Plugins**

3. Click **Add a New Plugin Directory**

4. Navigate to and select the `InteractiveHtmlBom-Enhanced` folder

5. Restart KiCad

6. Access via **Tools → Interactive HTML BOM**

### Method 2: Copy to KiCad Plugins Folder (KiCad 6 and older)

1. Clone or download this repository:
   ```bash
   git clone https://github.com/andrespineda/InteractiveHtmlBom-Enhanced.git
   ```

2. Copy the entire `InteractiveHtmlBom` folder to your KiCad plugins directory:

   **Windows:**
   ```
   C:\Users\<username>\Documents\KiCad\<version>\plugins\InteractiveHtmlBom
   ```

   **Linux/macOS:**
   ```
   ~/.local/share/kicad/<version>/plugins/InteractiveHtmlBom
   ```

3. Restart KiCad

4. Access via **Tools → Interactive HTML BOM**

## Using the Part Search Feature

### Quick Start

1. **Generate BOM**: Use InteractiveHtmlBom to generate your BOM HTML file
2. **Open BOM**: Open the generated HTML file in your browser
3. **Select Component**: Click on any component row in the BOM table to select it
4. **Search Parts**: Click the **🔍 Parts** button in the BOM toolbar
5. **View Results**: The search panel will open with pre-filled value and footprint
6. **Choose Supplier**: Select which suppliers to search (JLCPCB, Digi-Key, Mouser)
7. **Review Results**: Browse matching components with stock and pricing information
8. **Purchase**: Click "View Part →" to go directly to the supplier's purchase page

### Search Options

| Option | Description |
|--------|-------------|
| **Component Value** | The component value (e.g., 100K, 1uF, 2.2nH) |
| **Footprint** | The package/footprint (e.g., 0402, 0603, SOIC-8) |
| **Component Type** | Optional filter: resistor, capacitor, inductor, etc. |
| **Suppliers** | Check which suppliers to search |

### Understanding Results

For **JLCPCB** searches, you'll see:
- **LCSC Part Number**: The JLCPCB catalog number (e.g., C106224)
- **Manufacturer**: Component manufacturer name
- **Part Number**: Manufacturer's part number
- **Stock**: Current stock level (green = in stock, red = out of stock)
- **Price**: Unit price in USD
- **Footprint**: Package type
- **Description**: Component description
- **View Part**: Direct link to JLCPCB purchase page

For **Digi-Key** and **Mouser**, you'll see:
- **Search Link**: Direct link to search results on the supplier's website
- **Description**: Link with search query pre-filled

## Keyboard Shortcuts

| Key | Action |
|------|---------|
| `Escape` | Close the part search panel |
| `Enter` | Execute part search |

## API Integration Details

### BOM Parts Sourcing API

This plugin now uses the **BOM Parts Sourcing API** server for all part searches. This provides:

- **CORS-free access** to all supplier APIs
- **Secure API key storage** on the server
- **Unified search interface** across all suppliers
- **Real-time stock and pricing** from all sources

### Configuration

You can configure the API server URL via:

1. **Command line**: `--api-url http://localhost:3000`
2. **Config file**: Edit `ibom.config.ini` and add:
   ```ini
   [part_search]
   api_base_url = http://localhost:3000
   ```

### Supplier-Specific Details

#### JLCPCB
- Uses JLCSearch API (free, no API key required)
- 1.5M+ parts database
- Returns LCSC part numbers for JLCPCB assembly

#### Digi-Key
- Requires API credentials (Client ID + Client Secret)
- Subscribe to "ProductInformation V4" API
- Returns real-time stock, pricing, and datasheets

#### Mouser
- Requires API key
- Returns real-time stock, pricing, and datasheets

---

## Understanding Results

For all suppliers, you'll see:
- **Part Number**: Manufacturer's part number
- **Manufacturer**: Component manufacturer
- **Description**: Component description from supplier
- **Stock**: Current stock level (green = in stock, red = out of stock)
- **Price**: Unit price in USD
- **Footprint/Package**: Package type
- **Datasheet**: Link to datasheet (when available)
- **View Part**: Direct link to supplier's purchase page

For **JLCPCB**, you'll also see:
- **LCSC Part Number**: The JLCPCB catalog number (e.g., C106224)

## Workflow Example

Here's a typical workflow for using the part search feature:

```
1. Open your PCB project in KiCad
   ↓
2. Run: Tools → Interactive HTML BOM
   ↓
3. Configure and generate the BOM HTML
   ↓
4. Open the generated HTML file
   ↓
5. Browse the BOM table for components to source
   ↓
6. Click on a component row (e.g., R10 - 100K, 0402)
   ↓
7. Click "🔍 Parts" button
   ↓
8. Search panel opens with "100K" and "0402" pre-filled
   ↓
9. Click "Search Components"
   ↓
10. Review results:
   - JLCPCB: C106224 (YAGEO) - 5000 in stock - $0.003
   - Digi-Key: Click to search
   - Mouser: Click to search
   ↓
11. Click "View Part →" on JLCPCB result
   ↓
12. Add part to JLCPCB cart or copy LCSC part number
   ↓
13. Repeat for other components
```

## Testing the Plugin

### Test Your Installation

1. Open KiCad
2. Open a test PCB project (or create a simple one)
3. Go to **Tools → Interactive HTML BOM**
4. Click "Generate" to create the BOM
5. Open the generated HTML file in your browser
6. Click on any component row
7. Click the "🔍 Parts" button
8. Verify the search panel opens with component details pre-filled
9. Try searching for a component value (e.g., "100K" or "1uF")
10. Verify results appear correctly

### Sample Component Values to Test

| Value | Footprint | Expected Results |
|--------|-------------|-------------------|
| 100K | 0402 | YAGEO RC0402FR-07100KL |
| 1uF | 0603 | Multiple ceramic capacitors |
| 2.2nH | 0402 | Multiple inductors |
| 10uF | 0402 | Multiple capacitors |

## Providing Feedback

### Found a Bug?

1. Check existing [issues](https://github.com/andrespineda/InteractiveHtmlBom-Enhanced/issues)
2. Create a new issue with:
   - KiCad version
   - Browser used
   - Detailed steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable

### Enhancement Ideas?

1. Check existing [issues](https://github.com/andrespineda/InteractiveHtmlBom-Enhanced/issues) and [pull requests](https://github.com/andrespineda/InteractiveHtmlBom-Enhanced/pulls)
2. Create a new issue with:
   - What enhancement you'd like
   - Why it would be useful
   - Any implementation ideas you have
   - Example use cases

### Feature Requests

We're particularly interested in:

- **Full Digi-Key/Mouser API integration** - Direct part lookups with pricing
- **Export to CSV with LCSC parts** - Bulk update your BOM with found parts
- **Part comparison** - Compare specifications of multiple parts
- **Alternatives suggestion** - Suggest equivalent parts from other suppliers
- **Order directly from BOM** - Generate JLCPCB CSV for assembly
- **Footprint auto-detection** - Extract footprint from KiCad library data
- **Historical search** - Remember previously searched parts
- **Batch search** - Search multiple components at once

## Troubleshooting

### "Search error: Failed to fetch" or connection errors

- Ensure the BOM Parts Sourcing API is running:
  ```bash
  cd bom-parts-sourcing && bun run dev
  ```
- Check the API URL configuration matches where the API is running
- Verify no firewall is blocking port 3000

### "🔍 Parts" button not visible

- Ensure you're using the enhanced version from this repository
- Check that the HTML file was generated after installation
- Try clearing browser cache and regenerating the BOM

### Search not returning results

- **For all suppliers**: Check your internet connection
- **For Digi-Key/Mouser**: Verify API keys are configured in the BOM Parts Sourcing API's `.env` file
- Try with simpler search terms (just value, or just footprint)
- Check that the component value format is correct (e.g., "100K" not "100 k")

### Digi-Key shows "not configured"

- Add your Digi-Key credentials to the BOM Parts Sourcing API's `.env` file
- Ensure you've subscribed to "ProductInformation V4" API in DigiKey developer portal
- Restart the API server after adding credentials

### Mouser shows "not configured"

- Add your Mouser API key to the BOM Parts Sourcing API's `.env` file
- Restart the API server after adding the key

### Part search panel doesn't open

- Check browser console for JavaScript errors (F12 → Console)
- Ensure no other scripts are conflicting
- Try in a different browser (Chrome, Firefox, Edge)

## Development

### Building from Source

1. Clone repository:
   ```bash
   git clone https://github.com/andrespineda/InteractiveHtmlBom-Enhanced.git
   cd InteractiveHtmlBom-Enhanced
   ```

2. No build process needed - the plugin is pure Python and JavaScript

3. Modifications:
   - **Backend logic**: `InteractiveHtmlBom/core/part_search.py`
   - **HTML UI**: `InteractiveHtmlBom/web/ibom.html`
   - **Python core**: `InteractiveHtmlBom/core/ibom.py`

## License

This project maintains the original MIT license from InteractiveHtmlBom. See `LICENSE` for more info.

## Credits

- **InteractiveHtmlBom**: Original plugin by [openscopeproject](https://github.com/openscopeproject/InteractiveHtmlBom)
- **JLCSearch API**: Provided by [tscircuit](https://docs.tscircuit.com/web-apis/jlcsearch-api)
- **KiCad**: Electronic Design Automation software

## Links

- [Repository](https://github.com/andrespineda/InteractiveHtmlBom-Enhanced)
- [Issues](https://github.com/andrespineda/InteractiveHtmlBom-Enhanced/issues)
- [Original InteractiveHtmlBom](https://github.com/openscopeproject/InteractiveHtmlBom)
- [Original Wiki](https://github.com/openscopeproject/InteractiveHtmlBom/wiki)
- [Demo](https://openscopeproject.org/InteractiveHtmlBomDemo/)
- [KiCad](https://www.kicad.org/)
