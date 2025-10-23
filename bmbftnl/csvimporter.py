import csv
from pathlib import Path
from typing import Union, List
from operator import attrgetter

from bmbftnl.participant import Participant
from charset_normalizer import from_path

def convert_enrollment_to_bool(status: str) -> bool:
    """Convert string representation of enrollment status to boolean

    :param status: string representation of enrollment status
    :type status: str
    :raises ValueError: Detection was not successful
    :return: True if enrolled, False otherwise
    :rtype: bool
    """
    if status.lower() in ["j", "ja", "y", "yes", "true", "t", "1"]:
        return True
    if status.lower() in ["n", "nein", "no", "false", "f", "0"]:
        return False
    raise ValueError(f"Unknown value {status} for enrollment status")


class CSVImporter:
    def __init__(self, path: Path):
        self.participants: List[Participant] = self.read_participants(path)
    
    def read_participants(self, path: Path) -> List[Participant]:
        """Import participants from a CSV file. Guess the 'dialect' used by reading the first 1024 bytes of the file.
        Allow for arbirtrary columns as long as 'name', 'standort' and 'eingeschrieben' are present.

        :param path: File path to CSV file
        :type path: Path
        :raises AssertionError: CSV file does not have column names
        :raises AssertionError: CSV file doesn't have mandatory field names 'name', 'standort' and 'eingeschrieben'
        :raises AssertionError: CSV file is empty
        :return: Imported participants
        :rtype: List[Participant]
        """
        list_of_participants: List[Participant] = []
        
        # determine encoding, because windows sucks and adds a BOM
        charset_match = from_path(path)
        charset_result = charset_match.best()

        with open(path, newline="", encoding=charset_result.encoding + ("-sig" if charset_result.bom else "")) as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
            csvfile.seek(0)

            print(f"INFO: Reading file {path} with delimiter '{dialect.delimiter}' and line ending {repr(dialect.lineterminator)} in {csvfile.encoding} encoding")

            reader = csv.DictReader(csvfile, dialect=dialect)

            if not reader.fieldnames:
                raise AssertionError(f"File {path} does not contain column names")
            
            expected_fieldnames: Set = {"name", "standort", "eingeschrieben"}
            common_fieldnames: Set = set(reader.fieldnames) & expected_fieldnames

            if len(common_fieldnames) != 3:
                raise AssertionError(f"Missing field names: {expected_fieldnames - common_fieldnames}")
            
            for row in reader:
                participant: Participant = Participant(row["name"], row["standort"], convert_enrollment_to_bool(row["eingeschrieben"]))
                list_of_participants.append(participant)
        
        if len(list_of_participants) == 0:
            raise AssertionError(f"No participants specified in {path}")
        
        return list_of_participants
    
    def sort_participants(self, by: Union[str, List[str]]) -> None:
        """Sort participant list in-place

        :param by: Attributes of `Participant` class to use for sorting
        :type by: Union[str, List[str]]
        """
        self.participants.sort(key=attrgetter(*by))

