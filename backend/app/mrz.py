import re
from typing import Any


# =========================================================
# MRZ CLEANING
# =========================================================

def clean_mrz_line(line: str) -> str:
    """
    Clean OCR output so that MRZ characters are easier to detect.

    MRZ normally contains:
        A-Z
        0-9
        <
    """

    if not line:
        return ""

    line = line.upper().strip()

    # Common OCR mistakes / symbols that should behave
    # like the MRZ filler character.
    replacements = {
        "«": "<",
        "‹": "<",
        "≤": "<",
        "—": "<",
        "–": "<",
        "_": "<",
        "−": "<",
        " ": "",
        "\t": "",
    }

    for old, new in replacements.items():
        line = line.replace(old, new)

    # Common OCR mistakes seen in passport MRZs.
    replacements = {
        "O": "0",
    }

    # Do NOT globally replace O -> 0 because names can contain O.
    # Instead, leave letters untouched here.

    line = re.sub(r"[^A-Z0-9<]", "", line)

    return line


# =========================================================
# MRZ NORMALIZATION
# =========================================================

def normalize_mrz_line(line: str) -> str:
    """
    Make a detected MRZ line closer to the standard 44-character
    TD3 passport format.
    """

    line = clean_mrz_line(line)

    if not line:
        return ""

    # Passport MRZ lines are normally 44 characters.
    #
    # OCR may sometimes produce one or two extra characters.
    # Keep the first 44 because the passport parser uses
    # fixed-width fields.
    return line[:44]


# =========================================================
# MRZ CHARACTER SCORE
# =========================================================

def mrz_character_score(line: str) -> float:
    """
    Estimate how strongly a line resembles an MRZ line.

    MRZ lines contain mostly:
        A-Z
        0-9
        <
    """

    if not line:
        return 0.0

    cleaned = clean_mrz_line(line)

    if not cleaned:
        return 0.0

    valid = sum(
        1
        for character in cleaned
        if character.isalpha()
        or character.isdigit()
        or character == "<"
    )

    length_score = min(len(cleaned) / 44.0, 1.0)
    valid_score = valid / max(len(cleaned), 1)

    filler_score = min(
        cleaned.count("<") / 8.0,
        1.0,
    )

    return (
        length_score * 0.45
        + valid_score * 0.35
        + filler_score * 0.20
    )


# =========================================================
# MRZ DETECTION
# =========================================================

def detect_mrz(text: str) -> dict[str, Any]:
    """
    Detect passport MRZ lines from OCR text.

    Detection is intentionally tolerant because Tesseract may:
    - remove '<'
    - merge spaces
    - add spaces
    - slightly damage characters
    - return MRZ lines with fewer than 44 characters
    """

    if not text:
        return {
            "detected": False,
            "lines": [],
            "confidence": "low",
            "reason": "No OCR text available.",
        }

    # -----------------------------------------------------
    # Prepare OCR lines
    # -----------------------------------------------------

    raw_lines = text.splitlines()

    lines: list[str] = []

    for raw_line in raw_lines:
        cleaned = clean_mrz_line(raw_line)

        if cleaned:
            lines.append(cleaned)

    if not lines:
        return {
            "detected": False,
            "lines": [],
            "confidence": "low",
            "reason": "OCR did not produce usable text lines.",
        }

    # -----------------------------------------------------
    # METHOD 1
    # Strong passport MRZ signature
    #
    # First line normally starts with:
    # P<
    # -----------------------------------------------------

    for index, line in enumerate(lines):

        if line.startswith("P<"):

            # Look for a second long line nearby.
            for second_index in range(
                index + 1,
                min(index + 4, len(lines)),
            ):

                second_line = lines[second_index]

                if len(line) >= 20 and len(second_line) >= 20:

                    return {
                        "detected": True,
                        "lines": [
                            normalize_mrz_line(line),
                            normalize_mrz_line(second_line),
                        ],
                        "confidence": "high",
                        "reason": (
                            "Passport MRZ detected from "
                            "the P< document-code pattern."
                        ),
                    }

    # -----------------------------------------------------
    # METHOD 2
    # Tolerant passport-code detection
    #
    # OCR sometimes changes:
    #
    # P<
    #
    # into:
    #
    # P
    # P0
    # P<
    # P<<
    # -----------------------------------------------------

    for index, line in enumerate(lines):

        if not line:
            continue

        starts_like_passport = (
            line.startswith("P")
            and len(line) >= 18
        )

        if not starts_like_passport:
            continue

        for second_index in range(
            index + 1,
            min(index + 4, len(lines)),
        ):

            second_line = lines[second_index]

            if len(second_line) < 18:
                continue

            # Second MRZ line normally contains numbers,
            # dates and filler characters.
            digit_count = sum(
                1
                for character in second_line
                if character.isdigit()
            )

            filler_count = second_line.count("<")

            if digit_count >= 3 or filler_count >= 2:

                return {
                    "detected": True,
                    "lines": [
                        normalize_mrz_line(line),
                        normalize_mrz_line(second_line),
                    ],
                    "confidence": "medium",
                    "reason": (
                        "Passport-like MRZ detected from "
                        "nearby structured lines."
                    ),
                }

    # -----------------------------------------------------
    # METHOD 3
    # Two long MRZ-like lines
    #
    # This is useful when OCR completely misses P<.
    # -----------------------------------------------------

    candidates: list[tuple[int, str, float]] = []

    for index, line in enumerate(lines):

        if len(line) < 20:
            continue

        score = mrz_character_score(line)

        filler_count = line.count("<")

        digit_count = sum(
            1
            for character in line
            if character.isdigit()
        )

        # A long line with MRZ filler characters or digits
        # is a useful candidate.
        if (
            len(line) >= 25
            and (
                filler_count >= 2
                or digit_count >= 3
            )
            and score >= 0.45
        ):
            candidates.append(
                (
                    index,
                    line,
                    score,
                )
            )

    # Find two candidates close to each other.
    for first_position in range(len(candidates)):

        first_index, first_line, first_score = (
            candidates[first_position]
        )

        for second_position in range(
            first_position + 1,
            len(candidates),
        ):

            second_index, second_line, second_score = (
                candidates[second_position]
            )

            # MRZ lines should be close together.
            if second_index - first_index > 3:
                continue

            combined_score = (
                first_score + second_score
            ) / 2

            if combined_score >= 0.50:

                return {
                    "detected": True,
                    "lines": [
                        normalize_mrz_line(first_line),
                        normalize_mrz_line(second_line),
                    ],
                    "confidence": "medium",
                    "reason": (
                        "Two nearby long MRZ-like "
                        "OCR lines were detected."
                    ),
                }

    # -----------------------------------------------------
    # METHOD 4
    # Single strong MRZ line
    #
    # This does NOT mean the passport is fully parsed.
    # It only means that MRZ-like content exists.
    # -----------------------------------------------------

    for line in lines:

        if len(line) < 30:
            continue

        filler_count = line.count("<")

        if (
            len(line) >= 35
            and filler_count >= 1
            and mrz_character_score(line) >= 0.55
        ):

            return {
                "detected": True,
                "lines": [
                    normalize_mrz_line(line)
                ],
                "confidence": "medium",
                "reason": (
                    "A strong passport MRZ-like "
                    "line was detected."
                ),
            }

    # -----------------------------------------------------
    # Nothing detected
    # -----------------------------------------------------

    return {
        "detected": False,
        "lines": [],
        "confidence": "low",
        "reason": "No MRZ detected.",
    }


# =========================================================
# MRZ CHECK DIGIT
# =========================================================

def calculate_check_digit(value: str) -> str:
    """
    Calculate ICAO MRZ check digit.

    Weights repeat:
        7, 3, 1
    """

    weights = [7, 3, 1]

    total = 0

    for index, character in enumerate(value):

        if character.isdigit():

            number = int(character)

        elif "A" <= character <= "Z":

            number = (
                ord(character)
                - ord("A")
                + 10
            )

        elif character == "<":

            number = 0

        else:

            number = 0

        total += (
            number
            * weights[index % 3]
        )

    return str(total % 10)


# =========================================================
# PASSPORT MRZ PARSER
# =========================================================

def parse_passport_mrz(
    lines: list[str],
) -> dict[str, Any]:

    if not lines:

        return {
            "success": False,
            "reason": "No MRZ lines supplied.",
        }

    # Clean all supplied lines.
    cleaned = [
        clean_mrz_line(line)
        for line in lines
        if line
    ]

    cleaned = [
        line
        for line in cleaned
        if line
    ]

    # -----------------------------------------------------
    # Need both passport MRZ lines for full parsing
    # -----------------------------------------------------

    if len(cleaned) < 2:

        return {
            "success": False,
            "partial": True,
            "reason": (
                "Passport MRZ detected, but both "
                "MRZ lines were not available."
            ),
            "lines": cleaned,
        }

    # -----------------------------------------------------
    # Normalize to standard TD3 width
    # -----------------------------------------------------

    line1 = normalize_mrz_line(cleaned[0])
    line2 = normalize_mrz_line(cleaned[1])

    # -----------------------------------------------------
    # Passport document code
    # -----------------------------------------------------

    document_code = line1[:2]

    document_code_valid = (
        document_code.startswith("P")
    )

    # -----------------------------------------------------
    # Issuing country
    # -----------------------------------------------------

    issuing_country = (
        line1[2:5]
        if len(line1) >= 5
        else ""
    )

    # -----------------------------------------------------
    # Name
    # -----------------------------------------------------

    name_section = (
        line1[5:]
        if len(line1) > 5
        else ""
    )

    name_parts = name_section.split("<<")

    surname = ""

    given_names = ""

    if len(name_parts) >= 1:

        surname = (
            name_parts[0]
            .replace("<", " ")
            .strip()
        )

    if len(name_parts) >= 2:

        given_names = (
            name_parts[1]
            .replace("<", " ")
            .strip()
        )

    # -----------------------------------------------------
    # Passport number
    # -----------------------------------------------------

    passport_number = (
        line2[:9]
        .replace("<", "")
        if len(line2) >= 9
        else ""
    )

    passport_number_check = (
        line2[9]
        if len(line2) >= 10
        else ""
    )

    # -----------------------------------------------------
    # Nationality
    # -----------------------------------------------------

    nationality = (
        line2[10:13]
        if len(line2) >= 13
        else ""
    )

    # -----------------------------------------------------
    # Date of birth
    # -----------------------------------------------------

    date_of_birth = (
        line2[13:19]
        if len(line2) >= 19
        else ""
    )

    birth_check = (
        line2[19]
        if len(line2) >= 20
        else ""
    )

    # -----------------------------------------------------
    # Sex
    # -----------------------------------------------------

    sex = (
        line2[20]
        if len(line2) >= 21
        else ""
    )

    # -----------------------------------------------------
    # Expiry date
    # -----------------------------------------------------

    expiry_date = (
        line2[21:27]
        if len(line2) >= 27
        else ""
    )

    expiry_check = (
        line2[27]
        if len(line2) >= 28
        else ""
    )

    # -----------------------------------------------------
    # Personal number
    # -----------------------------------------------------

    personal_number = (
        line2[28:42]
        .replace("<", "")
        if len(line2) >= 42
        else ""
    )

    # =====================================================
    # CHECK DIGITS
    # =====================================================

    passport_number_valid = None

    if (
        passport_number
        and passport_number_check.isdigit()
    ):

        passport_number_valid = (
            calculate_check_digit(
                line2[:9]
            )
            == passport_number_check
        )

    birth_date_valid = None

    if (
        len(date_of_birth) == 6
        and birth_check.isdigit()
    ):

        birth_date_valid = (
            calculate_check_digit(
                date_of_birth
            )
            == birth_check
        )

    expiry_date_valid = None

    if (
        len(expiry_date) == 6
        and expiry_check.isdigit()
    ):

        expiry_date_valid = (
            calculate_check_digit(
                expiry_date
            )
            == expiry_check
        )

    # =====================================================
    # PARSE SUCCESS
    # =====================================================

    success = (
        document_code_valid
        and len(line1) >= 25
        and len(line2) >= 25
    )

    # =====================================================
    # RESULT
    # =====================================================

    return {
        "success": success,

        "documentCode": document_code,

        "documentCodeValid": document_code_valid,

        "issuingCountry": issuing_country,

        "surname": surname,

        "givenNames": given_names,

        "passportNumber": passport_number,

        "nationality": nationality,

        "dateOfBirth": date_of_birth,

        "sex": sex,

        "expiryDate": expiry_date,

        "personalNumber": personal_number,

        "checkDigits": {
            "passportNumber": passport_number_check,
            "passportNumberValid": passport_number_valid,

            "dateOfBirth": birth_check,
            "dateOfBirthValid": birth_date_valid,

            "expiryDate": expiry_check,
            "expiryDateValid": expiry_date_valid,
        },

        "lines": [
            line1,
            line2,
        ],
    }