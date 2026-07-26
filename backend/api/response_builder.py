from typing import Any

def success_response(
        result: Any,
        message: str= "Success"
):
    return {
        "success": True,
        "message": message,
        "result": result
    }

def error_response(
        message: str,
        errors= None
):
    response= {
        "success": False,
        "message": message
    }

    if errors:
        response["errors"]= errors

    return response