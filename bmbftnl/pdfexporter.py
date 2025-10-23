from datetime import date, timedelta
from itertools import cycle
from math import ceil
from pathlib import Path
from typing import List, Tuple, Dict

from bmbftnl.csvimporter import CSVImporter
from bmbftnl.participant import Participant
from pypdf import PdfReader, PdfWriter
from tqdm import tqdm

class PDFExporter:
    pdf_form_mapping: List[Tuple[str]] = [
        ("6", "20", "21", "Studierenderja  nein1"),
        ("19", "40", "41", "fill_0"),
        ("18", "39", "22", "fill_2"),
        ("17", "42", "23", "fill_4"),
        ("16", "43", "24", "fill_6"),
        ("15", "44", "25", "fill_8"),
        ("14", "45", "26", "fill_10"),
        ("13", "46", "27", "fill_12"),
        ("12", "Text7", "28", "fill_14"),
        ("11", "29", "34", "fill_16"),
        ("10", "30", "35", "fill_18"),
        ("9", "31", "36", "fill_20"),
        ("8", "32", "37", "fill_22"),
        ("7", "33", "38", "VO in Verbinduragten weiterg"),
    ]    

    def __init__(
        self,
        title: str,
        organization: str,
        start_date: date,
        end_date: date,
        participants: CSVImporter,
        template: Path,
        blank_pages: int = 1,
    ):
        """
        Constructor

        :param title: Name of event
        :type title: str
        :param organization: Organization hosting event
        :type organization: str
        :param start_date: Start date (inclusive)
        :type start_date: date
        :param end_date: End date of event (inclusive)
        :type end_date: date
        :param participants: List of participants
        :type participants: CSVImporter
        :param template: Path to PDF template, must have fillable form fields
        :type template: Path
        :param blank_pages: Number of blank pages to append to each day, defaults to 1
        :type blank_pages: int, optional
        """
        self.title: str = title
        self.organization: str = organization
        self.start_date: date = start_date
        self.end_date: date = end_date
        self.printable_participants: List[Dict] = self.import_participants(participants)
        self.template: Path = template
        self.blank_pages: int = blank_pages
    
    def import_participants(self, participants: CSVImporter) -> List[Dict]:
        printable_participants: List[Dict] = []

        for idx, (participant, form_ids) in enumerate(zip(participants.participants, cycle(PDFExporter.pdf_form_mapping))):
            assert isinstance(participant, Participant), "Participant list not consisting of objects of type Participant"

            printable_participants.append({
                form_ids[0]: idx + 1,
                form_ids[1]: participant.name,
                # set font size to 8 for default font because autosizing does not work
                # longest string without cutoff: Rheinland-Pfälzische Technische Universität Kaiserslautern-Landau
                form_ids[2]: (participant.location, "", 8),
                form_ids[3]: participant.printable_enrollment()
            })
        
        return printable_participants

    def generate_page_header(self, page_number: int, event_date: date) -> Dict[str, str]:
        """
        Generate general header information placed on every page

        :param page_number: Page number
        :type page_number: int
        :param event_date: Date to print on page
        :type event_date: date
        :return: Mapped values to correct PDF form field IDs
        :rtype: Dict[str, str]
        """
        return {
            "1": page_number,
            "2": self.start_date.strftime(r"%d.")
            + "-"
            + self.end_date.strftime(r"%d.%m.%y"),
            "3": event_date.strftime(r"%d.%m.%Y"),
            "4": self.organization,
            "5": self.title,
        }

    def generate_bmbf_list(self, output_directory: Path) -> None:
        """
        Generate BMBF attendence lists for every day of an event as seperate output files.
        A file is genereated for every day, there's currently no mechanism to skip specific dates.

        :param output_directory: Output directory to store all output files
        :type output_directory: Path
        """
        event_duration: timedelta = self.end_date - self.start_date
        num_pages_per_day: int = ceil(
            len(self.printable_participants) / len(PDFExporter.pdf_form_mapping)
        )

        pdf_reader: PdfReader = PdfReader(self.template)

        for event_day in tqdm(
            range(event_duration.days + 1), desc="Processing event", unit="file"
        ):
            pdf_writer: PdfWriter = PdfWriter()

            event_date: date = self.start_date + timedelta(days=event_day)

            for page in range(num_pages_per_day):
                chunk_start: int = page * len(PDFExporter.pdf_form_mapping)
                chunk_end: int = chunk_start + len(PDFExporter.pdf_form_mapping)
                chunk_of_participants: List[Dict] = {
                    k: v
                    for participant in self.printable_participants[chunk_start:chunk_end]
                    for k, v in participant.items()
                }

                pdf_writer.append(pdf_reader)

                pdf_writer.update_page_form_field_values(
                    pdf_writer.pages[page],
                    self.generate_page_header(page + 1, event_date),
                    auto_regenerate=False,
                )

                pdf_writer.update_page_form_field_values(
                    pdf_writer.pages[page], chunk_of_participants, auto_regenerate=False
                )

                pdf_writer.reset_translation(pdf_reader)

            for blank in range(self.blank_pages):
                pdf_writer.append(pdf_reader)

                pdf_writer.update_page_form_field_values(
                    pdf_writer.pages[num_pages_per_day + blank],
                    self.generate_page_header(num_pages_per_day + blank + 1, event_date),
                    auto_regenerate=False,
                )

                pdf_writer.reset_translation(pdf_reader)

            file_name: str = (
                self.title.replace(" ", "")
                + "-"
                + event_date.strftime(r"%d_%m_%y")
                + ".pdf"
            )
            with open(output_directory / file_name, mode="wb") as out_stream:
                pdf_writer.write(out_stream)

            pdf_writer.close()
        pdf_reader.close()