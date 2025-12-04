## Snelstart voor Windows Gebruikers

Als je de foutmelding krijgt: `ModuleNotFoundError: No module named '_study_path'`

**Snelle oplossing:**

1. Open Command Prompt in de `Codempose` map
2. Voer uit:
   ```cmd
   python fix_windows_install.py
   ```

Dit script detecteert en repareert automatisch veelvoorkomende Windows installatie problemen.

**Volledige installatie instructies:** Zie [INSTALL_WINDOWS.md](INSTALL_WINDOWS.md)

---

## Voor Eerste Installatie

### Stap 1: Extract
```cmd
tar -xzf codempose_complete_distribution_*.tar.gz
cd Codempose
```

### Stap 2: Installeer Dependencies
```cmd
pip install -r requirements.txt
```

Of gebruik het geautomatiseerde script:
```cmd
install_windows.bat
```

### Stap 3: Test
```cmd
python studies\eightyfirst.py
```

Als dit werkt, ben je klaar! 🎉

---

## Veelvoorkomende Problemen

| **Probleem** | **Oplossing** |
|-------------|--------------|
| `_study_path` niet gevonden | `python fix_windows_install.py` |
| Permission denied | `attrib -h -s -r studies\_study_path.py` |
| Oude versie conflict | Verwijder oude map volledig: `rmdir /S /Q Codempose` |
| Tar niet gevonden | Gebruik 7-Zip in plaats van tar commando |

---

## Support Files in Deze Distributie

- **INSTALL_WINDOWS.md** - Gedetailleerde Windows installatie instructies
- **fix_windows_install.py** - Geautomatiseerd probleem oplosser
- **install_windows.bat** - Windows installatie script
- **README.md** - Algemene documentatie
- **SETUP.md** - Setup instructies voor ontwikkelaars

---

## Next Steps

Na succesvolle installatie:

1. **Bekijk voorbeelden:**
   ```cmd
   python studies\eightyfirst.py
   python studies\102th.py
   ```

2. **Maak je eerste studie:**
   ```cmd
   python generate_study.py
   ```

3. **Lees documentatie:**
   - Station 1/2 workflow: `studies/102th.py` (regels 130-290)
   - Transformatie systeem: `DOCUMENTATION/`
   - Voorbeelden: `studies/`

---

**Versie:** November 2025  
**Features:** Station 2 Snippet Library, Windows Support, Blueprint Framework
