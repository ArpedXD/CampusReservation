class BlankInputsError(Exception):
    """RAISES IF THE INPUTS ARE BLANK"""
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)

class WrongData(Exception):
    """RAISE IF THERE ARE MISTAKES IN FORMAT"""
    def __init__(self, *args):
        super().__init__(*args)