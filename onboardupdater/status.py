class Status:
    def __init__(self, state: str):
        self.state = state
        self.rauc_state = ""
        self.last_error = ""
        self.boot_state = ""
