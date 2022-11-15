from dataclasses import dataclass


@dataclass
class NisraUpdateCheckConfig:
    survey_type: str
    bucket_file_type: str
    max_hours_since_last_update: int
    no_update_template_id: str
    missing_questionnaire_template_id: str

    def __init__(self):
        self.survey_type = "LMS"
        self.bucket_file_type = "bdbx"
        self.max_hours_since_last_update = 23
        self.no_update_template_id = "94264180-7ebd-4ff9-8a27-52abb5949c78"
        self.missing_questionnaire_template_id = "f9292929-8763-4147-ad1a-681398e8d9fc"
