# InteractiveHtmlBom-Enhanced

Enhanced version of InteractiveHtmlBom with integrated Digi-Key and JLCPCB part search functionality.

![icon](https://i.imgur.com/js4kDOn.png)

This is a fork of the excellent [InteractiveHtmlBom](https://github.com/openscopeproject/InteractiveHtmlBom) plugin for KiCad, with added **component parts search functionality** that allows you to quickly find and purchase components from major suppliers directly from the generated BOM HTML page.

## What's New

### 🔍 Component Parts Search

The enhanced version adds a powerful part search feature that integrates directly with:

- **JLCPCB** - Full API integration using the free JLCSearch API with real-time stock and pricing
- **Digi-Key** - Direct search link to Digi-Key's component catalog
- **Mouser** - Direct search link to Mouser's component catalog

#### Key Features:

- **Pre-filled search**: Clicking the "🔍 Parts" button automatically pre-fills the component value and footprint from the selected BOM row
- **Real-time LCSC parts**: JLCPCB search shows LCSC part numbers, stock levels, and pricing
- **Multi-supplier search**: Search multiple suppliers simultaneously with one click
- **Smart caching**: Search results are cached to avoid repeated API calls
- **Stock awareness**: See at a glance which parts are in stock
- **One-click purchase**: Direct links to purchase pages for each supplier

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

### JLCPCB / JLCSearch API

The enhanced version uses the **JLCSearch API** (provided by tscircuit) for JLCPCB part searches:

- **Free to use** - No API key required
- **Real-time data** - Live stock and pricing from JLCPCB
- **1.5M+ parts** - Comprehensive component database
- **No CORS issues** - Works directly from browser

**API Endpoint**: `https://jlcsearch.tscircuit.com/components/list.json`

### Digi-Key Integration

Digi-Key search redirects to Digi-Key's website with pre-filled search parameters. For full API integration with direct part lookups, a server-side backend would be required.

**Direct Search URL**: `https://www.digikey.com/en/products/filter?keywords=<search>`

### Mouser Integration

Mouser search redirects to Mouser's website with pre-filled search parameters. For full API integration, a server-side backend would be required.

**Direct Search URL**: `https://www.mouser.com/ProductSearch/?Keyword=<search>`

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

### "🔍 Parts" button not visible

- Ensure you're using the enhanced version from this repository
- Check that the HTML file was generated after installation
- Try clearing browser cache and regenerating the BOM

### Search not returning results

- **For JLCPCB**: Check your internet connection, the API is online
- **For Digi-Key/Mouser**: These are search links - verify the URL opens correctly
- Try with simpler search terms (just value, or just footprint)
- Check that the component value format is correct (e.g., "100K" not "100 k")

### Part search panel doesn't open

- Check browser console for JavaScript errors (F12 → Console)
- Ensure no other scripts are conflicting
- Try in a different browser (Chrome, Firefox, Edge)

### Slow search performance

- **First search**: May be slower as caches are built
- **Subsequent searches**: Will be faster due to caching
- **JLCPCB API**: Typically responds in 1-3 seconds
- Clear cache: Reload the HTML page to reset the cache

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
