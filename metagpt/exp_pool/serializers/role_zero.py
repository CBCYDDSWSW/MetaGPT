"""RoleZero Serializer."""

import copy
import json

from metagpt.exp_pool.serializers.simple import SimpleSerializer


class RoleZeroSerializer(SimpleSerializer):
    def serialize_req(self, req: list[dict]) -> str:
        """Serialize the request for database storage, ensuring it is a string.

        Only extracts the necessary content from `req` because `req` may be very lengthy and could cause embedding errors.

        Args:
            req (list[dict]): The request to be serialized. Example:
                [
                    {"role": "user", "content": "..."},
                    {"role": "assistant", "content": "..."},
                    {"role": "user", "content": "context"},
                    {"role": "user", "content": "context exp part"},
                ]

        Returns:
            str: The serialized request as a JSON string.
        """
        if not req:
            return ""

        filtered_req = self._filter_req(req)
        filtered_req.append(req[-1])

        return json.dumps(filtered_req)

    def _filter_req(self, req: list[dict]) -> list[dict]:
        """Filter the `req` to include only necessary items.

        Args:
            req (list[dict]): The original request.

        Returns:
            list[dict]: The filtered request.
        """

        filtered_req = [
            copy.deepcopy(item) for item in req if "Command Editor.read executed: file_path" in item["content"]
        ]

        return filtered_req
