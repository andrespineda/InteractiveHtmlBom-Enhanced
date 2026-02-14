# 🚀 InteractiveHtmlBom-Enhanced - Session Checkpoint

> **Quick Start**: Read this file first when starting a new session to get up to speed quickly.

---

## 📋 Project Overview

**Purpose**: KiCad plugin for generating interactive HTML BOMs with integrated part search functionality across JLCPCB, Digi-Key, and Mouser.

**Repository**: https://github.com/andrespineda/InteractiveHtmlBom-Enhanced

**Tech Stack**: Python 3, JavaScript, HTML/CSS, KiCad Plugin API

**Depends On**: [BOM Parts Sourcing API](https://github.com/andrespineda/bom-parts-sourcing) (must be running)

---

## ✅ Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| **JLCPCB Search** | ✅ Working | Via BOM Parts Sourcing API |
| **Digi-Key Search** | ✅ Working | Via BOM Parts Sourcing API |
| **Mouser Search** | ✅ Working | Via BOM Parts Sourcing API |
| **Plugin Installation** | ✅ Working | KiCad 6+ and 7+ |
| **CORS Issues** | ✅ Fixed | All requests proxied through API |

---

## 🔧 Architecture

```
┌─────────────────────────────────────┐
│  KiCad PCB File                     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  InteractiveHtmlBom Plugin          │
│  (Python + HTML/JS)                 │
│                                     │
│  • Parse PCB data                   │
│  • Generate interactive HTML BOM    │
│  • Inject part search UI            │
└──────────────┬──────────────────────┘
               │
               │ HTTP requests
               ▼
┌─────────────────────────────────────┐
│  BOM Parts Sourcing API             │
│  (localhost:3000)                   │
│                                     │
│  • JLCPCB (JLCSearch)               │
│  • Digi-Key (ProductInfo V4)        │
│  • Mouser (Search API)              │
└─────────────────────────────────────┘
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `InteractiveHtmlBom/core/part_search.py` | API client for BOM Parts Sourcing |
| `InteractiveHtmlBom/core/config.py` | Plugin configuration (includes `api_base_url`) |
| `InteractiveHtmlBom/core/ibom.py` | Main BOM generation logic |
| `InteractiveHtmlBom/web/ibom.html` | HTML template with part search UI |
| `InteractiveHtmlBom/__init__.py` | Plugin entry point |
| `README.md` | User documentation |

---

## ⚙️ Configuration

### API Server URL

The plugin connects to the BOM Parts Sourcing API. Configure via:

1. **Command line**:
   ```bash
   python -m InteractiveHtmlBom --api-url http://localhost:3000
   ```

2. **Config file** (`ibom.config.ini`):
   ```ini
   [part_search]
   api_base_url = http://localhost:3000
   ```

### Default Value

```
http://localhost:3000
```

---

## 🔌 Dependencies

### Required

- **BOM Parts Sourcing API** must be running:
  ```bash
  git clone https://github.com/andrespineda/bom-parts-sourcing.git
  cd bom-parts-sourcing
  bun install
  bun run dev
  ```

### Optional (for full functionality)

Configure in BOM Parts Sourcing API's `.env`:
- `DIGIKEY_CLIENT_ID` and `DIGIKEY_CLIENT_SECRET` - For Digi-Key searches
- `MOUSER_API_KEY` - For Mouser searches
- JLCPCB works without any API keys (free JLCSearch API)

---

## 📝 Sessions Summary

### Session 1: Initial Fork
- Forked InteractiveHtmlBom from openscopeproject
- Added basic part search with JLCPCB (JLCSearch)
- Added Digi-Key and Mouser links (not API integrated)
- **Issue**: JLCPCB CORS bug - direct browser calls blocked

### Session 2: Direct API Attempt
- Tried to add Digi-Key and Mouser API calls directly in Python
- **Issue**: CORS still blocked browser requests
- **Issue**: Digi-Key V3 endpoint deprecated
- **Issue**: Mouser endpoint wrong

### Session 3: API Server Integration ✅
- **Solution**: Use BOM Parts Sourcing API as proxy server
- Updated `part_search.py` with `BOMPartsSourcingClient`
- Updated JavaScript to call API instead of direct fetch
- Added configurable `api_base_url`
- All CORS issues resolved
- Full Digi-Key V4 and Mouser integration working

---

## 🐛 Known Issues / Gotchas

1. **API must be running**: If BOM Parts Sourcing API is not running, part search will fail with connection error
2. **API keys needed for Digi-Key/Mouser**: JLCPCB works without keys, but Digi-Key and Mouser require API credentials in the server
3. **Same origin policy**: The HTML BOM is opened as a local file (`file://`), so API must allow CORS (already handled by BOM Parts Sourcing API)
4. **Cache**: Search results are cached in browser memory - reload page to clear

---

## 🏃 Quick Commands

```bash
# Clone and setup
git clone https://github.com/andrespineda/InteractiveHtmlBom-Enhanced.git

# Install in KiCad (method 1 - plugin directory)
# Copy to KiCad plugins folder:
# Windows: C:\Users\<user>\Documents\KiCad\<version>\plugins\
# Linux: ~/.local/share/kicad/<version>/plugins/

# Start the API server (required)
cd ../bom-parts-sourcing && bun run dev

# Test
# 1. Open KiCad
# 2. Open a PCB project
# 3. Tools → Interactive HTML BOM
# 4. Generate BOM
# 5. In browser, click "🔍 Parts" button
```

---

## 🔗 Related Repositories

| Repository | Purpose | Status |
|------------|---------|--------|
| [bom-parts-sourcing](https://github.com/andrespineda/bom-parts-sourcing) | Server-side API for part searches | ✅ Active |
| [InteractiveHtmlBom-Enhanced](https://github.com/andrespineda/InteractiveHtmlBom-Enhanced) | This project (KiCad plugin) | ✅ Active |
| [bom-sourcing-utility](https://github.com/andrespineda/bom-sourcing-utility) | Python CLI for BOM sourcing | ✅ Complete |

---

## 📝 For New Sessions

When starting a new session:
1. Read this `CHECKPOINT.md` file
2. Ensure BOM Parts Sourcing API is running
3. Check `git log --oneline -5` for recent changes
4. Key files to understand:
   - `InteractiveHtmlBom/core/part_search.py` - API client
   - `InteractiveHtmlBom/web/ibom.html` - UI with JavaScript

---

## 🚧 Future Enhancements

- [ ] Add BOM upload button in plugin UI
- [ ] Export BOM with LCSC parts pre-filled
- [ ] Remember API server URL in plugin settings
- [ ] Show API connection status in UI
- [ ] Add batch search for entire BOM

---

*Last updated: Session 3 (February 2026)*
