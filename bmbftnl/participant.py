class Participant:
    def __init__(self, name: str, location: str, enrolled: bool):
        self.name: str = name
        self.location: str = location
        self.enrolled: bool = enrolled
    
    def printable_enrollment(self) -> str:
        """
        Convert enrollment status to suitable character representation for form filling
        :return: Aligned string to correctly fill field
        :rtype: str
        """
        return "  X" if self.enrolled else "            X"