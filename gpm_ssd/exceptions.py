import typeguard

@typeguard.typechecked()
class HttpException(Exception):
    
    # creates a readable error message from error dictionaty
    # example error dict:
    # { "username": ["This field is required."] }
    @staticmethod
    def from_error_dict(error_dict: dict):
        error_msg = ""
        for key, value in error_dict.items():
            error_msg = f"- {key}: "
            for error_detail in value:
                error_msg += f"{error_detail} "
            error_msg += "\n"