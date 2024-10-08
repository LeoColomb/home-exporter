#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import functools
import time
from typing import Any, Optional

import requests

# from . import LOGGER

class BaseAPI(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def api(self) -> str:
        raise NotImplementedError()

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token: Optional[str] = None
        self._last_request: Optional[float] = None
        self._access_expires: Optional[float] = None

    def request(self, verb: str, *args: Any, **kwargs: Any) -> Any:
        headers = kwargs.setdefault("headers", {})
        headers["Authorization"] = f"Bearer {self.access_token}"
        headers["Accept"] = "application/json"
        if self._last_request is not None:
            time.sleep(min(max(time.time() - self._last_request, 1), 1))
        resp = requests.request(verb, *args, **kwargs)
        self._last_request = time.time()
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            print(e)
            # LOGGER.error(resp.json())
        return resp.json()

    get = functools.partialmethod(request, "GET")
    post = functools.partialmethod(request, "POST")
    put = functools.partialmethod(request, "PUT")

    @property
    def access_token(self) -> str:
        if self._access_token is None or (
            self._access_expires is not None and self._access_expires < time.time()
        ):
            self._access_token, self._access_expires = self._authenticate()
        return self._access_token

    def _authenticate(self) -> tuple[str, float]:
        resp = requests.post(
            f"{self.api}/oauth2/v3/token",
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        token = data["access_token"]
        assert isinstance(token, str)
        expires_in = data["expires_in"]
        assert isinstance(expires_in, int)
        access_expires = time.time() + expires_in
        return (token, access_expires)

    def daily_consumption(
        self,
        usage_point_id: str,
        from_date: str,
        to_date: str
    ) -> Any:
        return self.get(
            f"{self.api}/metering_data_dc/v5/daily_consumption",
            params={
                "usage_point_id": usage_point_id,
                "start": from_date,
                "end": to_date,
            },
        )

    def consumption_load_curve(
        self,
        usage_point_id: str,
        from_date: str,
        to_date: str
    ) -> Any:
        return self.get(
            f"{self.api}/metering_data_clc/v5/consumption_load_curve",
            params={
                "usage_point_id": usage_point_id,
                "start": from_date,
                "end": to_date,
            },
        )

    def daily_consumption_max_power(
        self,
        usage_point_id: str,
        from_date: str,
        to_date: str
    ) -> Any:
        return self.get(
            f"{self.api}/metering_data_dcmp/v5/daily_consumption_max_power",
            params={
                "usage_point_id": usage_point_id,
                "start": from_date,
                "end": to_date,
            },
        )

class StagingAPI(BaseAPI):
    api = "https://gw.ext.prod-sandbox.api.enedis.fr"


class API(BaseAPI):
    api = "https://gw.ext.prod.api.enedis.fr"
