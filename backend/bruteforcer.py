import requests
import os
import time
import json
import logging

# Configure Brute Forcer logging
logging.basicConfig(level=logging.INFO)
scan_logger = logging.getLogger(__name__)

class BruteForcer:
    def __init__(self, output_filename='outputs_bruteforcer/brute_results.json'):
        self.scan_target = ''
        self.payloads = []
        self.auth_cookies = {}
        self.exclude_status_codes = []
        self.include_status_codes = []
        self.content_length_filter = None
        self.network_proxy = ''
        self.custom_params = {}
        self.display_results_live = False

        # Runtime data
        self.total_scan_time = 0.0
        self.rate_of_requests = 0.0
        self.scan_report = []
        self.report_file = output_filename
        self.number_of_payloads = 0

    def parse_auth_cookies(self, cookie_string):
        if not cookie_string:
            return {}

        cookies = {}
        for item in cookie_string.split(';'):
            if '=' in item:
                key, value = item.strip().split('=', 1)
                cookies[key] = value
        return cookies

    def send_request(self, url, params=None):
        try:
            headers = {'User-Agent': 'TRACE BruteForcer 1.0'}
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            # Defaulting to GET method
            response = requests.get(
                url,
                params=params,
                cookies=self.auth_cookies,
                proxies={'http': self.network_proxy, 'https': self.network_proxy} if self.network_proxy else None,
                timeout=5,
                headers=headers
            )

            content = response.text
            return {
                'status_code': response.status_code,
                'length': len(response.content),
                'error': False
            }

        except requests.RequestException as e:
            scan_logger.error(f"Request error: {e}")
            return {
                'status_code': 0,
                'length': 0,
                'error': True
            }

    def display_bruteforcer_results(self, result):
        if self.exclude_status_codes and result['status_code'] in self.exclude_status_codes:
            return False

        if self.include_status_codes and result['status_code'] not in self.include_status_codes:
            return False
        if self.content_length_filter is not None:
            if result['length'] != self.content_length_filter:
                return False
        return True

    def save_report_to_json(self):
        try:
            with open(self.report_file, 'w') as json_file:
                json.dump(self.scan_report, json_file, indent=4)
        except Exception as e:
            scan_logger.error(f"Error saving results as JSON file: {e}")

    async def run_scan(self, scan_parameters):
        self.configure_scan_parameters(scan_parameters)
        if not self.payloads:
            self.payloads = ['test', 'admin', 'password', '123456']
        self.number_of_payloads = len(self.payloads)

        start = time.time()
        processed_requests = 0
        filtered_requests = 0

        for i, payload in enumerate(self.payloads):
            url = os.path.join(self.scan_target, payload)
            result = self.send_request(url)
            processed_requests += 1

            result_entry = {
                'id': i + 1,
                'response': result['status_code'],
                'payload': payload,
                'length': result['length'],
                'error': result['error']
            }

            if self.display_bruteforcer_results(result):
                self.scan_report.append(result_entry)
                filtered_requests += 1

            elapsed = time.time() - start
            requests_per_second = processed_requests / elapsed if elapsed > 0 else 0

            update = {
                "progress": (i + 1) / self.number_of_payloads,
                "processed_requests": processed_requests,
                "filtered_requests": filtered_requests,
                "requests_per_second": round(requests_per_second, 2)
            }

            if self.display_results_live:
                update.update(result_entry)

            yield update

        if not self.display_results_live:
            for result in self.scan_report:
                yield result

        end = time.time()
        self.total_scan_time = end - start
        self.rate_of_requests = round(processed_requests / self.total_scan_time, 2) if self.total_scan_time > 0 else 0
        self.save_report_to_json()

    def configure_scan_parameters(self, scan_params):
        self.scan_target = scan_params.get('target_url', '')

        if 'word_list' in scan_params and scan_params['word_list']:
            word_list_param = scan_params['word_list']
            scan_logger.info(f"Processing wordlist parameter: {word_list_param}")
            
            if isinstance(word_list_param, list):
                self.payloads = word_list_param
                scan_logger.info(f"Using list of {len(self.payloads)} payloads")
            elif isinstance(word_list_param, str):
                if os.path.exists(word_list_param):
                    try:
                        with open(word_list_param, 'r') as file:
                            self.payloads = [line.strip() for line in file if line.strip()]
                        scan_logger.info(f"Loaded {len(self.payloads)} payloads from file: {word_list_param}")
                    except Exception as e:
                        scan_logger.error(f"Error reading wordlist file: {e}")
                        self.payloads = [word_list_param]  # Use as single item if error occurs
                else:
                    self.payloads = [word_list_param]
                    scan_logger.info(f"Using single payload: {word_list_param}")

        if 'hide_status' in scan_params and scan_params['hide_status']:
            try:
                self.exclude_status_codes = [int(code.strip()) for code in scan_params['hide_status'].split(',') if code.strip()]
            except ValueError:
                scan_logger.warning("Invalid hide_status format. Expected comma-separated integers.")

        if 'show_status' in scan_params and scan_params['show_status']:
            try:
                self.include_status_codes = [int(code.strip()) for code in scan_params['show_status'].split(',') if code.strip()]
            except ValueError:
                scan_logger.warning("Invalid show_status format. Expected comma-separated integers.")

        if 'filter_by_content_length' in scan_params and scan_params['filter_by_content_length']:
            try:
                self.content_length_filter = int(scan_params['filter_by_content_length'])
            except ValueError:
                scan_logger.warning("Invalid filter_by_content_length format. Expected integer.")

        if 'proxy' in scan_params and scan_params['proxy']:
            self.network_proxy = scan_params['proxy']

        if 'show_results' in scan_params:
            self.display_results_live = scan_params.get('show_results', True)

        if 'additional_parameters' in scan_params and scan_params['additional_parameters']:
            if isinstance(scan_params['additional_parameters'], dict):
                self.custom_params = scan_params['additional_parameters']
            elif isinstance(scan_params['additional_parameters'], str):
                try:
                    self.custom_params = dict(item.split('=') for item in scan_params['additional_parameters'].split('&') if '=' in item)
                except:
                    scan_logger.warning("Invalid additional_parameters format. Expected param1=value1&param2=value2")
