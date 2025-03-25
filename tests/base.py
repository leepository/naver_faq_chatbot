class TestBase:

    ACCESS_TOKEN = None

    def run_request(self, test_client, method, url, headers=None, params=None, data=None, files=None, formdata=False):
        access_token = self.ACCESS_TOKEN

        # Header
        if headers is None:
            headers = {}
        if access_token is not None:
            headers.update({'authorization': f'Bearer {access_token}'})

        test_client_method = {
            "GET": test_client.get,
            "POST": test_client.post,
            "PUT": test_client.put,
            "PATCH": test_client.patch,
            "DELETE": test_client.delete
        }
        if method.upper() in ['GET', 'DELETE']:
            resp = test_client_method[method.upper()](
                url=url,
                headers=headers,
                params=params
            )
        else:
            resp = test_client_method[method.upper()](
                url=url,
                headers=headers,
                params=params,
                json=data if formdata is False else None,
                data=data if formdata is True else None,
                files=files
            )

        result_dict = {}
        if resp.status_code not in [200, 201]:
            try:
                result_dict.update({
                    'status_code': resp.status_code,
                    'detail': resp.json()
                })
            except:
                result_dict.update({
                    'status_code': resp.status_code,
                    'detail': resp.text
                })
        else:
            try:
                result_dict.update({
                    'status_code': resp.status_code,
                    'data': resp.json()
                })
            except:
                result_dict.update({
                    'status_code': resp.status_code,
                    'data': resp.text
                })

        return result_dict
