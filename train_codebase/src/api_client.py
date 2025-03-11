#!/usr/bin/env python3
"""
API client utilities.
"""

import time
import json
import requests

class APIClient:
    """Client for making API requests."""
    
    def __init__(self, base_url, api_key=None, timeout=10):
        """Initialize the API client."""
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        # BUG: Should validate base_url format
    
    def get_headers(self):
        """Get request headers."""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if self.api_key:
            # BUG: Hardcoded header format, should be configurable
            headers['Authorization'] = f'Bearer {self.api_key}'
        return headers
    
    def make_request(self, method, endpoint, data=None, params=None):
        """Make an API request."""
        url = f"{self.base_url}/{endpoint}"
        headers = self.get_headers()
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params,
                timeout=self.timeout
            )
            # BUG: Should check status code before returning response
            return response.json()
        except requests.exceptions.RequestException as e:
            # BUG: Should raise a custom exception instead of returning an error dict
            return {'error': str(e)}
    
    def get(self, endpoint, params=None):
        """Make a GET request."""
        return self.make_request('GET', endpoint, params=params)
    
    def post(self, endpoint, data=None):
        """Make a POST request."""
        return self.make_request('POST', endpoint, data=data)
    
    def put(self, endpoint, data=None):
        """Make a PUT request."""
        return self.make_request('PUT', endpoint, data=data)
    
    def delete(self, endpoint):
        """Make a DELETE request."""
        # BUG: No way to send data with DELETE request
        return self.make_request('DELETE', endpoint)
    
    def retry_request(self, method, endpoint, data=None, params=None, max_retries=3, backoff=1):
        """Make a request with retry logic."""
        retries = 0
        # BUG: No jitter in backoff timing - could cause thundering herd issues
        while retries < max_retries:
            response = self.make_request(method, endpoint, data, params)
            if 'error' not in response:
                return response
            
            retries += 1
            if retries < max_retries:
                time.sleep(backoff * retries)
        
        return response