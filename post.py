import requests
class Post:
    def __init__(self):
        self.data_url = "https://api.npoint.io/dd33828d26d7ea2c36ef"


    def get_data(self):
        response = requests.get(url=self.data_url)
        data = response.json()
        return data
