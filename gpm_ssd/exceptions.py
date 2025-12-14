import typeguard

@typeguard.typechecked()
class HttpException(Exception):
    
    @staticmethod
    def from_error_dict(error_dict: dict):
        error_msg = ""
        for key, value in error_dict.items():
            error_msg += f"- {key}: "
            for error_detail in value:
                error_msg += f"{error_detail} "
            error_msg += "\n"
        return HttpException(error_msg)