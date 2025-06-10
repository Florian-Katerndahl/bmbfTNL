# bmbfTNL -- Automatisches Erstellen von Teilnehmendenlisten für das BMBF

`bmbfTNL` ist eine Pythonanwendung für die Kommandozeile um automatisch Teilnehmendenlisten für Veranstaltungen, welche durch das BMBF geförtdert werden auszufüllen. **`bmbftnl` ist kein offizielles Tool des BMBF und wurde nicht in Kooperation mit diesem entwickelt. Verwendung auf eigene Verantwortung!**

## Installation

```bash
pip install bmbftnl
```

## Nutzung

Zum einfachen Erstellen der Teilnehmendenlisten wird das Programm `bmbftnl` auf der Kommandozeile aufgerufen. Die verpflichtenden und optionalen Argumente sind unten aufgeführt. Die Teilnehmendenliste muss wie drei Spalten (name, standort und eingeschrieben) haben -- ein Beispiel findet du weiter unten.

> [!NOTE]
> Das Programm wurde mit Vorlagen aus dem Jahr 2018/2019 und 2024/2025 getestet. Einige sehr lange Standortnamen (> 65 Zeichen) können unter Umständen in der Liste abgeschnitten werden.

```bash
usage: bmbftnl [-h] --titel TITEL --organisation ORGANISATION --beginn BEGINN --ende ENDE --teilnehmende TEILNEHMENDE --vorlage VORLAGE [--extra-seiten EXTRA_SEITEN] out_dir

Automatisches Ausfüllen von Teilnehmendenlisten des BMBF mit Namen, Standort und Studierendenstatus

positional arguments:
  out_dir               Pfad zu Verzeichnis, in welchem Dateien abgespeichert werden sollen (aktuelles Verzeichnis mit Punkt angeben)

options:
  -h, --help            show this help message and exit
  --titel TITEL         Titel der Veranstaltung
  --organisation ORGANISATION
                        Ausrichtende Organisation
  --beginn BEGINN       Beginn der Veranstaltung im ISO-Format (yyyy-mm-dd)
  --ende ENDE           Ende der Veranstaltung im ISO-Format (yyyy-mm-dd)
  --teilnehmende TEILNEHMENDE
                        CSV-Tabelle mit den Spalten name, standort und immatrikuliert. Letzteres durch ja/nein angegeben
  --vorlage VORLAGE     Dateipfad zu der vom BMBF erstellten Vorlage. Zuletzt getestest mit Vorlage 2024/2025
  --extra-seiten EXTRA_SEITEN
                        Anzahl an Leerseiten pro Tag, die hinzugefügt werden
```

```csv
name,standort,eingeschrieben
Max Mustermann,Universität zu Musterstadt,ja
Marie Musterfrau,Andere Universität,ja
Jonathan Musterperson,Universität Musterstadt,nein
```

## Lizenz

`bmbftnl` ist unter der MIT Lizenz lizensiert.

## Danksagung

Die Idee für `bmbftnl` kommt von Jörn Tillmanns, dessen Version du [hier](https://gitlab.fachschaften.org/kif/bmbf) findest. `bmbftnl` vereinfacht die Anwendung durch die Bereitstellung eines Kommandozeilenprogramms sowie der Entfernung von externen Programmen.
