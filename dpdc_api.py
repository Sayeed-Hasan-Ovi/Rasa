import requests

__AUTH_USER = "9267"
__AUTH_TOKEN = "9267@#"
__BASE_URL = "https://api.dpdc.org.bd/api/bot/"

class DPDCAPIException(Exception):
    """Base exception for DPDC API errors."""

class DPDCNetworkException(DPDCAPIException):
    """Network related error."""

class DPDCResponseException(DPDCAPIException):
    """Invalid/Unexpected response from DPDC API."""

def validate_phone(phone_number):
    try:
        return __call_api("botUserValidation", {
        "authusr": __AUTH_USER,
        "authtoken": __AUTH_TOKEN,
        "mob": bangla_to_english(phone_number)
    })
    except DPDCNetworkException:
        return {"error": "Network unavailable. Please check your connection or try again later."}
    except DPDCResponseException:
        return {"error": "DPDC system returned an invalid response. Please try again later."}
    except DPDCAPIException:
        return {"error": "Something went wrong while processing your request."}


def billing_information(bill_number):
    try:
        return __call_api("botGetBillInfo", {
        "authusr": __AUTH_USER,
        "authtoken": __AUTH_TOKEN,
        "billno": bangla_to_english(bill_number)
    })
    except DPDCNetworkException:
        return {"error": "Network unavailable. Please check your connection or try again later."}
    except DPDCResponseException:
        return {"error": "DPDC system returned an invalid response. Please try again later."}
    except DPDCAPIException:
        return {"error": "Something went wrong while processing your request."}


def customer_information(customer_number, phone_number):
    try:
        return __call_api("botGetCustInfo", {
        "authusr": __AUTH_USER,
        "authtoken": __AUTH_TOKEN,
        "mob": bangla_to_english(phone_number),
        "custno": bangla_to_english(customer_number)
    })
    except DPDCNetworkException:
        return {"error": "Network unavailable. Please check your connection or try again later."}
    except DPDCResponseException:
        return {"error": "DPDC system returned an invalid response. Please try again later."}
    except DPDCAPIException:
        return {"error": "Something went wrong while processing your request."}


def prepaid_information(customer_number, sequence):
    try:
        return __call_api("botGetPrepaidInfo", {
        "authusr": __AUTH_USER,
        "authtoken": __AUTH_TOKEN,
        "custno": bangla_to_english(customer_number),
        "seqNumber": sequence
    })  
    except DPDCNetworkException:
        return {"error": "Network unavailable. Please check your connection or try again later."}
    except DPDCResponseException:
        return {"error": "DPDC system returned an invalid response. Please try again later."}
    except DPDCAPIException:
        return {"error": "Something went wrong while processing your request."}


def online_new_connection_information(tracking_number):
    try:
        return __call_api("botGetOncInfo", {
        "authusr": __AUTH_USER,
        "authtoken": __AUTH_TOKEN,
        "trackingNumber": bangla_to_english(tracking_number)
    })
    except DPDCNetworkException:
        return {"error": "Network unavailable. Please check your connection or try again later."}
    except DPDCResponseException:
        return {"error": "DPDC system returned an invalid response. Please try again later."}
    except DPDCAPIException:
        return {"error": "Something went wrong while processing your request."}


def register_complaint(phone_number, customer_number, complaintType):
    try:
        return __call_api("botComplain", {
        "authusr": __AUTH_USER,
        "authtoken": __AUTH_TOKEN,
        "mob": bangla_to_english(phone_number),
        "custno": bangla_to_english(customer_number),
        "complainttype": complaintType,
        "address":"",
        "nocs":"D1"
    })
    except DPDCNetworkException:
        return {"error": "Network unavailable. Please check your connection or try again later."}
    except DPDCResponseException:
        return {"error": "DPDC system returned an invalid response. Please try again later."}
    except DPDCAPIException:
        return {"error": "Something went wrong while processing your request."}

def register_complaint_new(phone_number, address, noc_name, complaintType):
    try:
        return __call_api("botComplain", {
        "authusr": __AUTH_USER,
        "authtoken": __AUTH_TOKEN,
        "mob": bangla_to_english(phone_number),
        "custno": "",
        "complainttype": complaintType,
        "address":address,
        "nocs":nocs[noc_name.lower()] if noc_name.lower() in nocs else "00"
    })
    except DPDCNetworkException:
        return {"error": "Network unavailable. Please check your connection or try again later."}
    except DPDCResponseException:
        return {"error": "DPDC system returned an invalid response. Please try again later."}
    except DPDCAPIException:
        return {"error": "Something went wrong while processing your request."}

def complaint_info(tracking_number):
    try:
        return __call_api("botGetComplaintInfo", {
        "authusr": __AUTH_USER,
        "authtoken": __AUTH_TOKEN,
        "trackingNumber": tracking_number
    })
    except DPDCNetworkException:
        return {"error": "Network unavailable. Please check your connection or try again later."}
    except DPDCResponseException:
        return {"error": "DPDC system returned an invalid response. Please try again later."}
    except DPDCAPIException:
        return {"error": "Something went wrong while processing your request."}


def __call_api(api, body):
    try:
        response = requests.post(f"{__BASE_URL}{api}", json=body, timeout=10)
        if not response.ok:
            raise DPDCResponseException(
                f"API {api} failed with status {response.status_code}: {response.text}"
            )

        results = response.json()
        if results and isinstance(results, list) and len(results) > 0:
            return results[0]

        raise DPDCResponseException(f"API {api} returned empty/invalid response: {results}")
    except requests.exceptions.RequestException as e:
        # Network issues (DNS, timeout, SSL error, no internet, etc.)
        raise DPDCNetworkException(f"Network error while calling {api}: {e}") from e
    except ValueError as e:
        # JSON parse error
        raise DPDCResponseException(f"Failed to parse response from {api}: {e}") from e


def bangla_to_english(bangla_number):
    bangla_to_english_map = {
        '০': '0',
        '১': '1',
        '২': '2',
        '৩': '3',
        '৪': '4',
        '৫': '5',
        '৬': '6',
        '৭': '7',
        '৮': '8',
        '৯': '9'
    }

    english_number = ''
    for char in bangla_number:
        if char in bangla_to_english_map:
            english_number += bangla_to_english_map[char]
        else:
            english_number += char

    return english_number


nocs = {
  "adabor": "G1",
  "azimpur": "D9",
  "banglabazar": "A6",
  "bangshal": "B6",
  "bashabo": "A9",
  "bonoshree": "F2",
  "demra": "E1",
  "dhanmondi": "D2",
  "fateullah": "B8",
  "jigatola": "D8",
  "jurain": "B3",
  "kakrail": "C6",
  "kamrangirchar": "F1",
  "kazla": "A4",
  "khilgaon": "A2",
  "lalbag": "A3",
  "maniknagar": "B2",
  "matuail": "E2",
  "moghbazar": "D1",
  "motijheel": "A1",
  "mugdapara": "B9",
  "n.gonj (east)": "B7",
  "n.gonj (west)": "A7",
  "narinda": "B1",
  "paribag": "C3",
  "postogola": "A5",
  "rajarbag": "D6",
  "ramna": "D3",
  "satmasjid": "C2",
  "shere b.nagar": "D5",
  "shyamoli": "D4",
  "shyampur": "B4",
  "shytalakha": "E3",
  "siddirgonj": "A8",
  "swamibag": "B5",
  "tejgaon": "C1"
}
