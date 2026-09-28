class BlankInputsError(Exception):
    """RAISES IF THE INPUTS ARE BLANK"""
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)