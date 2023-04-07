import requests
import logging
import os
from json import JSONDecodeError

logging.basicConfig(level=logging.DEBUG)

API_URL = os.environ.get("API_URL", "https://rest.nexmo.com/sms/json")
TIMEOUT = os.environ.get("API_TIMEOUT", 10)

# mapping of incoming parameters to the ones expected by the external API
RENAME_PARAMS = {
    "dst_phone": "to",
    "src_phone": "from",
    "message": "text",
}


def result(success=False, error_msg="Unknown error", **kwargs):
    """Create a structure to be sent as a JSON response"""
    # return all additional keys, but override status & error
    kwargs["success"] = success
    if error_msg:
        kwargs["error"] = error_msg
    else:
        kwargs.pop("error", None)
    return kwargs


def send_message(request):
    """Get incoming request and send a request to external API"""

    # unique ID of each request to simplify troubleshooting
    trace_id = request.headers.get("X-Portaone-Trace-Id", None)
    # include it into log entries
    log_id = f"REQ <{trace_id}>"

    request_json = request.get_json()

    # Re-map parameters from incoming JSON data
    payload = {
        outgoing: request_json[incoming]
        for incoming, outgoing in RENAME_PARAMS.items()
        if incoming in request_json
    }
    logging.info(f"{log_id} Sending message: {payload}")
    # add auth info
    auth = request_json.get("auth_info", {})
    payload["api_key"] = auth.get("login", "")
    secret = auth.get("password", None)
    if not secret:
        secret = auth.get("token", None)
    payload["api_secret"] = secret
    if not payload["api_key"] or not payload["api_secret"]:
        err_msg = f"{log_id} Missing auth info in {auth}"
        logging.info(err_msg)
        return result(error_msg=err_msg)

    try:
        # Send HTTP request to external server
        response = requests.post(
            API_URL,
            timeout = TIMEOUT,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=payload,
        )
    except requests.exceptions.Timeout:
        err_msg = f"{log_id} Connection to {API_URL} timed out"
        logging.info(err_msg)
        return result(error_msg=err_msg)
    except requests.exceptions.RequestException as e:
        err_msg = f"{log_id} Request error: {e}"
        logging.info(err_msg)
        return result(error_msg=err_msg)

    if response.status_code != 200:
        err_msg = f"{log_id} Request failed: {response.status_code} {response.text}"
        logging.info(err_msg)
        return result(error_msg=err_msg)

    # check the returned result
    try:
        response_json = response.json()
    except JSONDecodeError:
        err_msg = f"{log_id} Response is not a valid JSON: {response.text}"
        logging.info(err_msg)
        return result(success=True, error_msg=err_msg)

    logging.info(f"{log_id} Message sent successfully: {response_json}")
    # API returns a list of messages, but we sent only one, so we can take the first
    msg_list = response_json.get("messages", [])
    if isinstance(msg_list, list) and len(msg_list) > 0:
        msg_id = msg_list[0].get("message-id", None)
    else:
        msg_id = None
    return result(success=True, error_msg=None, message_id=msg_id)
