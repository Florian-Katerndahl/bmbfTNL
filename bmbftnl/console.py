from argparse import ArgumentParser
from datetime import date
from pathlib import Path
from bmbftnl.participants import Teilnehmendenliste

def main() -> int:
    arguments = ArgumentParser(
        description="Automatisches Ausfüllen von Teilnehmendenlisten des BMBF mit Namen, Standort und Studierendenstatus"
    )
    arguments.add_argument(
        "--titel",
        required=True,
        type=str,
        help="Titel der Veranstaltung"
    )
    arguments.add_argument(
        "--organisation",
        required=True,
        type=str,
        help="Ausrichtende Organisation"
    )
    arguments.add_argument(
        "--beginn",
        required=True,
        type=str,
        help="Beginn der Veranstaltung im ISO-Format (yyyy-mm-dd)"
    )
    arguments.add_argument(
        "--ende",
        required=True,
        type=str,
        help="Ende der Veranstaltung im ISO-Format (yyyy-mm-dd)"
    )
    arguments.add_argument(
        "--teilnehmende",
        required=True,
        type=Path,
        help="CSV-Tabelle mit den Spalten name, standort und eingeschrieben. Letzteres durch ja/nein angegeben"
    )
    arguments.add_argument(
        "--vorlage",
        required=True,
        type=Path,
        help="Dateipfad zu der vom BMBF erstellten Vorlage. Zuletzt getestest mit Vorlage 2024/2025"
    )
    arguments.add_argument(
        "--extra-seiten",
        type=int,
        default=1,
        help="Anzahl an Leerseiten pro Tag, die hinzugefügt werden"
    )
    arguments.add_argument(
        "out_dir",
        type=Path,
        help="Pfad zu Verzeichnis, in welchem Dateien abgespeichert werden sollen (aktuelles Verzeichnis mit Punkt angeben)"
    )

    cli_args = arguments.parse_args()

    assert cli_args.teilnehmende.exists(), "Teilnehmendenverzeichnis existiert nicht"
    assert cli_args.vorlage.exists(), "Vorlage exisitiert nicht"
    assert cli_args.out_dir.exists() and cli_args.out_dir.is_dir(), "Ausgabeverzeichnis existiert nicht oder ist kein Verzeichnis"

    start_date: date = date.fromisoformat(cli_args.beginn)
    end_date: date = date.fromisoformat(cli_args.ende)

    tnl = Teilnehmendenliste(
        cli_args.titel,
        cli_args.organisation,
        start_date,
        end_date,
        cli_args.teilnehmende,
        cli_args.vorlage,
        cli_args.extra_seiten
    )

    tnl.generate_bmbf_list(cli_args.out_dir)
