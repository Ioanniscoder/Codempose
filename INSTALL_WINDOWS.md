# Windows Installatie Instructies

## Stap 1: Extract de Tarball

### Optie A: Met 7-Zip (Aanbevolen)
1. Download en installeer 7-Zip: https://www.7-zip.org/
2. Rechtermuisklik op `codempose_complete_distribution_*.tar.gz`
3. Selecteer: **7-Zip → Extract Here**
4. Dit maakt een `.tar` bestand
5. Rechtermuisklik opnieuw op het `.tar` bestand
6. Selecteer: **7-Zip → Extract Here**

### Optie B: Met Windows Tar (Windows 10+)
Open PowerShell of Command Prompt in de map met de tarball:
```cmd
tar -xzf codempose_complete_distribution_20251114_220027.tar.gz
```

## Stap 2: Verwijder Oude Installatie (BELANGRIJK!)

Als je een oude versie hebt, moet je deze VOLLEDIG verwijderen:

### Methode 1: Met Command Prompt (Veilig)
```cmd
cd C:\Users\johan\OneDrive - Unipat B.V\Personal\Scores
rmdir /S /Q Codempose
```

### Methode 2: Met Explorer
1. Als normale delete niet werkt, gebruik Shift+Delete (bypass Recycle Bin)
2. Als `_study_path.py` blijft hangen:
   ```cmd
   cd Codempose\studies
   attrib -h -s -r _study_path.py
   del _study_path.py
   ```

## Stap 3: Extract Opnieuw

Voer extractie opnieuw uit (zie Stap 1).

## Stap 4: Installeer Python Dependencies

```cmd
cd Codempose
pip install -r requirements.txt
```

## Stap 5: Test de Installatie

```cmd
python studies/eightyfirst.py
```

## Veelvoorkomende Problemen

### `ModuleNotFoundError: No module named '_study_path'`
- **Oorzaak**: Oude `_study_path.py` bleef hangen bij vorige installatie
- **Oplossing**: Volg Stap 2 volledig, dan opnieuw Stap 1

### `Permission Denied` bij verwijderen
- **Oorzaak**: Windows heeft bestand als "systeem" gemarkeerd
- **Oplossing**: 
  ```cmd
  attrib -h -s -r Codempose\studies\_study_path.py
  attrib -h -s -r Codempose\studies\__init__.py
  ```

### Tar commando niet gevonden
- **Oorzaak**: Oude Windows versie (< Windows 10)
- **Oplossing**: Gebruik 7-Zip (Optie A)

## Python Virtuele Omgeving (Optioneel maar Aanbevolen)

```cmd
cd Codempose
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Verificatie Checklist

Na installatie, controleer dat deze bestanden bestaan:

```
Codempose\
├── src\
│   ├── __init__.py
│   ├── score_builder.py
│   └── project_template.py
├── studies\
│   ├── __init__.py
│   ├── _study_path.py          ← BELANGRIJK!
│   ├── eightyfirst.py
│   └── 102th.py
├── requirements.txt
└── README.md
```

Controleer met PowerShell:
```powershell
Test-Path Codempose\studies\_study_path.py
```
Moet `True` teruggeven.

## Support

Als deze instructies niet werken:
1. Controleer Windows versie: `winver`
2. Controleer Python versie: `python --version` (moet 3.8+ zijn)
3. Stuur screenshot van error naar ontwikkelaar
