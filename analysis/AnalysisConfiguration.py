class AnalysisConfiguration:
    def __init__(self, participants, general_overwrite, accumulation_overwrite, directed_mask_overwrite,
                 validation_overwrite, saliency, accumulation_mapping, accumulated_weight_type,
                 directed_weight_type):
        self.participants = participants
        self.general_overwrite = general_overwrite
        self.accumulation_overwrite = accumulation_overwrite or general_overwrite
        self.directed_mask_overwrite = directed_mask_overwrite or general_overwrite or accumulation_overwrite
        self.validation_overwrite = validation_overwrite or general_overwrite or accumulation_overwrite or directed_mask_overwrite
        self.saliency = saliency
        self.accumulation_mapping = accumulation_mapping
        self.accumulated_weight_type = accumulated_weight_type
        self.directed_weight_type = directed_weight_type