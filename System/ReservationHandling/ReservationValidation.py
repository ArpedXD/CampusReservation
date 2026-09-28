class ReservationValidation:
    def ValidateReservation():
        pattern = r"^(0[1-9]|1[0-2]):[0-5][0-9](AM|PM)-(0[1-9]|1[0-2]):[0-5][0-9](AM|PM)$"
        if not re.fullmatch(pattern, payload["time"]):
            return self._reservation_error.setText("Please Follow this format : 00:00AM-00:00AM")