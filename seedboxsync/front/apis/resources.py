# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2026 Guillaume Kulakowski <guillaume@kulakowski.fr>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
#
import uuid
from flask_restx import fields, Model, Namespace, Resource as RestXResource
from typing import Any
from datetime import datetime


class Resource(RestXResource):  # type: ignore[misc]
    """
    Base Resource class extending Flask-RestX Resource.

    Provides utility methods for:
    - enforcing limits on query parameters
    - building consistent API response envelopes
    - generating envelope models for Swagger documentation
    """

    def set_limit(self, limit: int) -> int:
        """
        Clamp the limit value within the allowed range [5, 1000].

        Args:
            limit (int): The requested limit value.

        Returns:
            int: The clamped limit within [5, 1000].
        """
        if limit < 5:
            return 5
        elif limit > 1000:
            return 1000
        return limit

    def build_envelope(
        self,
        data: Any,
        *,
        type: str = "about:blank",
        status_code: int = 200,
        message: str | None = None,
        data_total: int | None = None,
    ) -> dict[str, Any]:
        """
        Build a standard API response envelope.

        Args:
            data (Any): The response payload.
            type (str): The resource type or endpoint identifier (default: 'about:blank').
            status_code (int): HTTP status code (default: 200).
            message (str): Send message in place of data.
            data_total (int | None): Optional total number of items if the result is paginated.

        Returns:
            dict[str, Any]: Structured API response containing metadata and payload.
        """
        return {
            "type": type,
            "success": True,
            "status": status_code,
            "timestamp": datetime.now().astimezone().isoformat(),
            "traceId": str(uuid.uuid4()),
            **({"data": data} if data is not None else {}),
            **({"data_total": data_total} if data_total is not None else {}),
            **({"message": message} if message is not None else {}),
            "data": data,
        }

    @staticmethod
    def build_envelope_model(
        api: Namespace,
        name: str,
        *,
        nested_model: Model | None = None,
        as_list: bool = True,
        as_message: bool = False,
    ) -> Model:
        """
        Build a Flask-RestX model for a standard API response envelope.

        This is used for Swagger documentation. You can generate an envelope
        for a single resource or for a list of resources.

        Args:
            api (Namespace): The Flask-RestX namespace.
            name (str): The name of the nested resource model.
            nested_model (Model): The Flask-RestX model representing the resource.
            as_list (bool): If True, the 'data' field will be a list of nested resources.
            as_message (bool): The response is a message only.
        Returns:
            Model: A new Flask-RestX model representing the envelope.
        """
        if as_message is False:
            if as_list:
                data_field = fields.List(
                    fields.Nested(nested_model),
                    required=True,
                    description=f"List of {name} objects",
                )
            else:
                data_field = fields.Nested(nested_model, required=True, description=f"The {name} object")
            data_total = fields.Integer(required=False, description=f"Total of {name} object")
            message_field = None
        else:
            data_field = None
            data_total = None
            message_field = fields.String(required=False, description="Response message", example="All is OK")

        return api.model(
            f"Envelope[{name}]",
            {
                "type": fields.String(
                    required=True,
                    description="Resource type or endpoint identifier",
                    example=name,
                ),
                "success": fields.Boolean(
                    required=True,
                    description="Indicates if the request succeeded",
                    example=True,
                ),
                "status": fields.Integer(required=True, description="HTTP status code", example=200),
                "timestamp": fields.DateTime(required=True, description="Timestamp of the response"),
                "traceId": fields.String(
                    required=True,
                    description="Unique trace identifier",
                    example="0a8ab95e-a463-424e-bc6d-505503bf200d",
                ),
                **({"data": data_field} if data_field is not None else {}),
                **({"data_total": data_total} if data_total is not None else {}),
                **({"message": message_field} if message_field is not None else {}),
            },
        )


class DateTimeOrZero(fields.DateTime):  # type: ignore[misc]
    def format(self, value: int | datetime) -> Any:
        if value == 0:
            return 0
        return super().format(value)
