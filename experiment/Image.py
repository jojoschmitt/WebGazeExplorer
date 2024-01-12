import os.path
import re

from util import repo_root, list_files

SPECIFICATIONS = {
    1: ["Community", "E-Commerce", "Entertainment", "Informational"],
    2: ["Kontaktformular", "Herunterladbare Inhalte", "Lesen von Informationen", "Login", "Zahlungsabwicklung", "Posten von Inhalten",
        "Registrierung", "Visueller Medienkonsum"],
    3: ["Karriereseite", "Gegenstand in den Einkaufswagen", "Startseite", "Login", "Logout", "Zahlungsabwicklung", "Posten von Inhalten",
        "Registrierung"]
}


class Image:
    def __init__(self, id, task_id, reference=False):
        self.id: int = id
        self.task_id: int = task_id
        self.reference: bool = reference  # Is reference image for task 3 or not
        self.url: str = self.__infer_url()
        self.specification_id: int = self.__specification_id_from_url()
        self.specification: str = self.__specification_from_specification_id()
        # Reference images only exist for task 3
        assert not reference or reference and self.task_id == 3

    def __infer_url(self):
        image_dir = os.path.join(repo_root, "experiment", "images")
        if self.reference:
            image_dir = os.path.join(image_dir, "reference")
        else:
            image_dir = os.path.join(image_dir, "original")
        image_dir = os.path.join(image_dir, f"task{self.task_id}")
        files = list_files(image_dir)
        image_url = os.path.join(image_dir, files[self.id])
        return image_url

    def __specification_from_specification_id(self):
        assert 0 < self.specification_id <= len(SPECIFICATIONS[self.task_id])
        return SPECIFICATIONS[self.task_id][self.specification_id-1]

    def __specification_id_from_url(self):
        match = re.search(".*-s(\d).*", self.url)
        assert match is not None
        specification_str = match[1]
        specification_id = int(specification_str)
        return specification_id

    def get_name(self):
        return os.path.basename(self.url)

    def get_host(self):
        split = self.get_name().split("-")
        # Make sure that no host contains a '-'
        assert len(split) == 2
        host = split[0]
        return host



