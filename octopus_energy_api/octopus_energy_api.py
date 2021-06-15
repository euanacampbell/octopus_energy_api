import requests
from requests.auth import HTTPBasicAuth
import json

class oe_api():

    def __init__(self, account_number, api_key, mpan=None, serial_number=None):
        
        self.account_number=account_number

        if not mpan and not serial_number:
            account_details = self.get_mpan_serial(account_number, api_key)

            self.mpan = account_details['mpan']
            self.serial_number = account_details['serial_numbers'][1]
        else:
            self.mpan = mpan
            self.serial_number = serial_number

        self.s = requests.session()
        self.s.auth = (api_key, "")

        self.base = "https://api.octopus.energy/v1"
    
    def _get(cls, url):
        
        response = cls.s.request(method="GET", url=url)

        parsed = response.json()

        return( parsed )

    def get_mpan_serial(self, account_number, api_key):
        """Optionally load additional account details if not provided"""

        # details = self.account_details(account_number=account_number)
        url=f"https://api.octopus.energy/v1/accounts/{account_number}"

        s = requests.session()
        s.auth = (api_key, "")
        response = s.request(method="GET", url=url)
        details = response.json()

        to_return={}

        # mpan
        mpan = details['properties'][0]['electricity_meter_points'][0]['mpan']
        to_return['mpan']=mpan

        # serial numbers
        meter_data = details['properties'][0]['electricity_meter_points'][0]['meters']
        serials=[]

        for meter in meter_data:
            serial = meter['serial_number']

            serials.append(serial)

        to_return['serial_numbers']=serials

        # return
        return(to_return)


    def account_details(self, account_number=None):
        
        if not account_number:
            account_number=self.account_number
        
        response = self._get(f"https://api.octopus.energy/v1/accounts/{account_number}")

        return(response)

    def products(self):

        response = self._get(f"https://api.octopus.energy/v1/products/?brand=OCTOPUS_ENERGY")

        return(response)

    def convert_datetime_to_tz(cls, time):
        
        format_tz='%Y-%m-%dT%H:%M:%S%z'

        return(time.strftime(format_tz))
    
    def consumption(self, start, end):
        
        start=self.convert_datetime_to_tz(start)
        end=self.convert_datetime_to_tz(end)

        url=self.base
        setup=f"/electricity-meter-points/{self.mpan}/meters/{self.serial_number}/consumption/"
        
        parameters=f"?page_size=10000&period_from={start}&period_to={end}&order_by=period"

        url=f"{self.base}{setup}{parameters}"

        response = self._get(url)

        return(response['results'])
