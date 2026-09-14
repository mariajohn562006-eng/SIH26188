import re


def clean_mrz_text(text: str) -> list[str]:
    """
    Clean OCR text and find possible MRZ lines.
    """

    lines = text.upper().splitlines()

    cleaned_lines = []

    for line in lines:
        # Remove spaces and characters that are unlikely in MRZ
        line = re.sub(r"[^A-Z0-9<]", "", line)

        if len(line) >= 30:
            cleaned_lines.append(line)

    return cleaned_lines


def detect_mrz(text: str):
    """
    Detect possible Machine Readable Zone (MRZ) lines.
    """

    lines = clean_mrz_text(text)

    # Passport MRZ normally contains two long lines.
    candidates = [
        line
        for line in lines
        if len(line) >= 40
    ]

    if len(candidates) >= 2:
        return {
            "detected": True,
            "lines": candidates[-2:]
        }

    return {
        "detected": False,
        "lines": []
    }


def parse_passport_mrz(mrz_lines: list[str]):
    """
    Parse a basic two-line passport MRZ (TD3).

    This extracts commonly useful fields when the MRZ
    is correctly detected.
    """

    if len(mrz_lines) != 2:
        return {
            "success": False,
            "reason": "Two MRZ lines are required"
        }

    line1 = mrz_lines[0]
    line2 = mrz_lines[1]

    # Passport MRZ should normally start with P<
    if not line1.startswith("P"):
        return {
            "success": False,
            "reason": "MRZ does not appear to be a passport MRZ"
        }

    # Document type
    document_type = line1[0:2]

    # Issuing country
    issuing_country = line1[2:5]

    # Names
    name_section = line1[5:]

    if "<<" in name_section:
        surname, given_names = name_section.split("<<", 1)

        surname = surname.replace("<", " ").strip()
        given_names = given_names.replace("<", " ").strip()
    else:
        surname = ""
        given_names = name_section.replace("<", " ").strip()

    # Second line
    document_number = line2[0:9].replace("<", "")
    nationality = line2[10:13]

    date_of_birth = line2[13:19]
    sex = line2[20:21]
    expiry_date = line2[21:27]

    return {
        "success": True,
        "documentType": document_type,
        "issuingCountry": issuing_country,
        "surname": surname,
        "givenNames": given_names,
        "documentNumber": document_number,
        "nationality": nationality,
        "dateOfBirth": date_of_birth,
        "sex": sex,
        "expiryDate": expiry_date
    }