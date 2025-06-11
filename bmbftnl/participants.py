from csv import DictReader
from datetime import date, timedelta
from itertools import cycle
from pathlib import Path
from math import ceil
from typing import List, Dict, Tuple
from operator import itemgetter

from pypdf import PdfReader, PdfWriter
from tqdm import tqdm


class Teilnehmendenliste:
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

    @classmethod
    def enrolled_to_printable(cls, enrolled: str) -> str:
        """
        Convert enrollment status to suitable character representation for form filling

        :param enrolled: Enrollment status
        :type enrolled: str
        :return: Aligned string to correctly fill field
        :rtype: str
        """
        return "  X" if enrolled.lower() == "ja" else "            X"

    @classmethod
    def read_participants(cls, participants: Path) -> List[Dict]:
        """
        Read participants, order them by location and replace csv
        field names by form names

        :param participants: File path to CSV file
        :type participants: Path
        :raises AssertionError: Field names not "name", "standort" and "eingeschrieben"
        :raises AssertionError: Empty participant list gien
        :return: List of participants dictionaries
        :rtype: List[Dict]
        """
        participant_list: List[Dict] = []
        with open(participants, encoding="utf-8") as csvfile:
            reader = DictReader(csvfile)

            if reader.fieldnames != ["name", "standort", "eingeschrieben"]:
                raise AssertionError(
                    "Column fields are expected to be name, standort and eingeschrieben"
                )

            participant_list = list(reader)

        # sort participants by location to make finding oneself in list easier
        participant_list.sort(key=itemgetter("standort", "name"))

        for number, (participant, form_ids) in enumerate(
            zip(participant_list, cycle(Teilnehmendenliste.pdf_form_mapping))
        ):
            participant_list[number][form_ids[0]] = number + 1
            participant_list[number][form_ids[1]] = participant["name"]
            # set font size to 8 for default font because autosizing does not work
            # longest string without cutoff: Rheinland-Pfälzische Technische Universität Kaiserslautern-Landau
            participant_list[number][form_ids[2]] = (participant["standort"], "", 8)
            participant_list[number][
                form_ids[3]
            ] = Teilnehmendenliste.enrolled_to_printable(participant["eingeschrieben"])
            del participant["standort"]
            del participant["name"]

        if len(participant_list) == 0:
            raise AssertionError("No participants specified")

        return participant_list

    def __init__(
        self,
        title: str,
        organization: str,
        start_date: date,
        end_date: date,
        participants: Path,
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
        :param participants: Path to CSV file with participants
        :type participants: Path
        :param template: Path to PDF template, must have fillable form fields
        :type template: Path
        :param blank_pages: Number of blank pages to append to each day, defaults to 1
        :type blank_pages: int, optional
        """
        self.title: str = title
        self.organization: str = organization
        self.start_date: date = start_date
        self.end_date: date = end_date
        self.participants: List[Dict] = Teilnehmendenliste.read_participants(
            participants
        )
        self.template: Path = template
        self.blank_pages: int = blank_pages

    def form_header_fields(self, page_number: int, event_date: date) -> Dict[str, str]:
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
        A file is genereated for every day, even if the specific day is not funded; there's
        currently no mechanism to skip specific dates.

        :param output_directory: Output directory to store all output files
        :type output_directory: Path
        """
        event_duration: timedelta = self.end_date - self.start_date
        num_pages_per_day: int = ceil(
            len(self.participants) / len(Teilnehmendenliste.pdf_form_mapping)
        )

        pdf_reader: PdfReader = PdfReader(self.template)

        for event_day in tqdm(
            range(event_duration.days + 1), desc="Processing event", unit="file"
        ):
            pdf_writer: PdfWriter = PdfWriter()

            event_date: date = self.start_date + timedelta(days=event_day)

            for page in range(num_pages_per_day):
                chunk_start: int = page * len(Teilnehmendenliste.pdf_form_mapping)
                chunk_end: int = chunk_start + len(Teilnehmendenliste.pdf_form_mapping)
                chunk_of_participants: List[Dict] = {
                    k: v
                    for participant in self.participants[chunk_start:chunk_end]
                    for k, v in participant.items()
                }

                pdf_writer.append(pdf_reader)

                pdf_writer.update_page_form_field_values(
                    pdf_writer.pages[page],
                    self.form_header_fields(page + 1, event_date),
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
                    self.form_header_fields(num_pages_per_day + blank + 1, event_date),
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
