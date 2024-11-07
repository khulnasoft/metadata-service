"""
Utility functions for the RAG flow integration tests.
"""

import json
from pydantic import ValidationError
from pydantic_core import to_jsonable_python
from typing import List, Type, get_origin, get_args, Any, Union, TypeVar
from tests.v1.integration.test_client import test_client

# Define a generic type variable for the response model
T = TypeVar("T")


def execute_and_validate_endpoint(
    url: str,
    request_obj: Any,
    response_model: Union[Type[T], Type[List[T]]],
    method: str = "POST",
    expected_status_code: int = 200,
) -> Union[T, List[T]]:
    """
    Executes an endpoint and validates the response structure against a Pydantic model.

    :param url: The endpoint URL to send the request to.
    :param request_obj: The request payload to send.
    :param response_model: The Pydantic model or list of models to validate the response against.
    :param method: The HTTP method to use for the request. Default is POST.
    :return: An instance or list of instances of the response_model populated with the response data.
    :raises AssertionError: If the response status code is not 200 or if validation fails.
    """
    response = None
    val = json.dumps(request_obj, default=to_jsonable_python)
    if method.upper() == "POST":
        response = test_client.post(
            url,
            content=val,
            headers={"content-type": "application/json"},
        )
    elif method.upper() == "GET":
        response = test_client.get(
            url, params=request_obj
        )  # Using request_obj as query parameters for GET
    elif method.upper() == "PUT":
        response = test_client.put(
            url,
            content=val,
            headers={"content-type": "application/json"},
        )
    elif method.upper() == "DELETE":
        response = test_client.delete(
            url,
            headers={"content-type": "application/json"},
        )
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")

    assert (
        response.status_code == expected_status_code
    ), f"Expected status code {expected_status_code} but received: {response.status_code}"

    response_data = response.json()

    try:
        # Check if the response_model is a list type
        if get_origin(response_model) is list:
            model = get_args(response_model)[0]
            return [model(**item) for item in response_data]
        elif isinstance(response_data, list):
            return [response_model(**item) for item in response_data]
        else:
            return response_model(**response_data)
    except ValidationError as e:
        assert False, f"Response structure validation failed: {e}"
