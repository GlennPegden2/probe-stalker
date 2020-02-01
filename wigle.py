import requests, json

class Wigle:

    AUTH            = 'Basic PUTYOURWIGLEAPIKEYHERE'
    ENDPOINT_SEARCH = 'https://api.wigle.net/api/v2/network/search'

    def wigle_location(ssid, wigle_flag):
        headers = {
            'accept': 'application/json',
            'authorization': Wigle.AUTH
            }
        payload = {
            'onlymine': False,
            'first': 0,
            'freenet': False,
            'paynet': False,
            'ssid': ssid,
            'latrange1': 53.1963, 
            'latrange2': 54.3967, 
            'longrange1': -2.5378, 
            'longrange2': -0.5603
        }
        try:
#            Wigle seem to have an invalid ssl cert  on their api endpoint. Please remove the next 2 line and uncomment the third one, once they've fixed it
            requests.packages.urllib3.disable_warnings()
            r = requests.get(Wigle.ENDPOINT_SEARCH, headers=headers, params=payload, verify=False)
#            r = requests.get(Wigle.ENDPOINT_SEARCH, headers=headers, params=payload)
        except:
            print(r)
            return 1
        res = json.loads(r.text)

        if 'message' in res:
            if res['message'] == 'too many queries today':
                return 3
        if not wigle_flag:
            if 'results' in res:
                if len(res['results']) > 40:
                    return 2
                else:
                    try:
                       return res['results'][-1]
                    except:
#                        print("No data - res minus 1")
#                        print(res)
                        return 2
            else:
                return None 
        else:
            return None
