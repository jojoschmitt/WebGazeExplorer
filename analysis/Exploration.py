from typing import Optional


class Exploration:
    """
    An exploration basically gives the timeframe in which one image has been presented to the user.
    The image can be inferred from the img_name
    """
    def __init__(self, trial_start, img_name, img_online, img_offline, trial_end):
        """
        Attributes are timestamps in microseconds (us)
        """
        self.trial_start: Optional[float] = trial_start
        self.img_name: Optional[str] = img_name
        self.img_online: Optional[float] = img_online
        self.img_offline: Optional[float] = img_offline
        self.trial_end: Optional[float] = trial_end

    def is_complete(self):
        if self.trial_start and self.img_name and self.img_online and self.img_offline and self.trial_end:
            return True
        return False

    def attribute_from_tsv(self, line):
        timestamp_str, msg = line.split("\t")
        timestamp = float(timestamp_str)
        if "TRIALSTART" in msg:
            self.trial_start = timestamp
            return
        if "IMAGENAME" in msg:
            self.img_name = msg.split(" ")[1].strip()
            return
        if "image online" in msg:
            self.img_online = timestamp
            return
        if "image offline" in msg:
            self.img_offline = timestamp
            return
        if "TRIALEND" in msg:
            self.trial_end = timestamp
            return
        raise ValueError("The line does not contain an exploration attribute.")

    @staticmethod
    def create_exploration():
        return Exploration(None, None, None, None, None)