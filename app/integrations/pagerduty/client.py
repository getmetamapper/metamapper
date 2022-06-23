# -*- coding: utf-8 -*-
from app.integrations.client import ApiClient


class PagerDutyClient(ApiClient):
    """Client for sending API calls to PagerDuty.
    """
    base_url = "https://events.pagerduty.com/v2/enqueue"

    def __init__(self, integration_key):
        self.integration_key = integration_key
        super().__init__()

    def request(self, method, path, headers=None, data=None, params=None):
        """Send an authenticated API request.
        """
        if not headers:
            headers = {"Content-Type": "application/json"}

        return self._request(method, path, headers=headers, json=data, params=params)

    def send_trigger(self, source, summary, severity, href, component=None, group=None, dedup_key=None):
        """Send a PagerDuty trigger alert.
        """
        payload = {
            "routing_key": self.integration_key,
            "event_action": "trigger",
            "dedup_key": dedup_key,
            "payload": {
                "summary": summary,
                "severity": severity,
                "source": source,
                "group": group,
                "component": component,
            },
            "links": [
                {
                    "href": href,
                    "text": "View in Metamapper",
                }
            ],
        }

        return self.post("/", data=payload)
