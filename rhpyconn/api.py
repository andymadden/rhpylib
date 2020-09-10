from urllib.request import urlopen, Request
from http.client import HTTPResponse
import json
import gzip
from uuid import uuid4
from datetime import datetime
import sqlite3

class RHConnection:
    def __init__(self, token=None, un=None, pw=None, mfa=None, user_agent=None, log_location=None):
        if log_location:
            self.log_db = sqlite3.connect('logs.sqlite3')
            self.log_cursor = self.log_db.cursor()
            
            self.log_cursor.execute("DROP TABLE IF EXISTS ConnectionLog;")
            self.log_cursor.execute("CREATE TABLE ConnectionLog (timestamp datetime, url text, request_headers text, request_body text, response_headers text, response_body text);")
            self.log_db.commit()

        if user_agent:
            self.user_agent = user_agent
        else:
            self.user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0"

        if token:
            self.token = token
        elif un and pw and mfa:
            auth = self.auth(un, pw, mfa)
            self.token = auth['token_type'] + ' ' + auth['access_token']
        else:
            auth = self.auth(input('Username: '), input('Password: '), input("MFA: "))
            self.token = auth['token_type'] + ' ' + auth['access_token']


        self.account = self.get_account()['results'][0]['id']
    
    def auth(self, un, pw, mfa):
        host = "api.robinhood.com"
        filename = "/oauth2/token/"

        req_body = json.dumps({
            "client_id": "c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS",
            "device_token": str(uuid4()),
            "expires_in": 86400,
            "grant_type": "password",
            "mfa_code": mfa,
            "password": pw,
            "scope": "internal",
            "username": un
        })

        req = Request('https://'+host+filename, headers={
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Length': str(len(req_body)),
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'Host': host,
            'Origin': 'https://robinhood.com',
            'Referer': 'https://robinhood.com',
            'TE': 'Trailers',
            'User-Agent': self.user_agent,
            'X-TimeZone-Id': 'America/Chicago'
        }, data=req_body.encode('utf-8'))
        resp = urlopen(req)
        resp_body = resp.read().decode('utf-8')

        return json.loads(resp_body)
    
    def get_account(self):
        host = "nummus.robinhood.com"
        filename = "/accounts/"

        req = Request('https://'+host+filename, headers={
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Authorization': self.token,
            'Connection': 'keep-alive',
            'Host': host,
            'Origin': 'https://robinhood.com',
            'Referer': 'https://robinhood.com',
            'TE': 'Trailers',
            'User-Agent': self.user_agent,
            'X-TimeZone-Id': 'America/Chicago'
        })
        
        resp = urlopen(req)
        resp_headers = str(resp.getheaders())
        resp_body = resp.read().decode('utf-8')

        if self.log_db:
            self.log_cursor.execute("""
                INSERT INTO ConnectionLog
                    (timestamp, url, request_headers, request_body, response_headers, response_body)
                VALUES
                    (?, ?, ?, ?, ?, ?);
            """, (datetime.now(), req.get_full_url(), json.dumps(req.headers), str(req.data), resp_headers, resp_body))
            self.log_db.commit()

        return json.loads(resp_body)
    
    def get_historical_data(self, guid, bounds, interval, span):
        host = "api.robinhood.com"
        filename = "/marketdata/forex/historicals/"+ guid +"/"
        # bounds=24_7, interval=hour, span=week
        # bounds=24_7, interval=15second, span=hour
        query = "?bounds="+bounds+"&interval="+interval+"&span="+span

        req = Request('https://'+host+filename+query, headers={
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'Authorization': self.token,
            'Connection': 'keep-alive',
            'Host': host,
            'Origin': 'https://robinhood.com',
            'Referer': 'https://robinhood.com',
            'TE': 'Trailers',
            'User-Agent': self.user_agent,
            'X-TimeZone-Id': 'America/Chicago'
        })
        resp = urlopen(req)
        resp_headers = resp.info()
        resp_body = gzip.decompress(resp.read()).decode('utf-8')

        if self.log_db:
            self.log_cursor.execute("""
                INSERT INTO ConnectionLog
                    (timestamp, url, request_headers, request_body, response_headers, response_body)
                VALUES
                    (?, ?, ?, ?, ?, ?);
            """, (datetime.now(), req.get_full_url(), json.dumps(req.headers), str(req.data), str(resp_headers), str(resp_body)))
            self.log_db.commit()

        return json.loads(resp_body)

    def get_quote(self, guid):
        host = "api.robinhood.com"
        filename = "/marketdata/forex/quotes/"+guid+"/"

        req = Request('https://'+host+filename, headers={
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'Authorization': self.token,
            'Connection': 'keep-alive',
            'Host': host,
            'Origin': 'https://robinhood.com',
            'Referer': 'https://robinhood.com',
            'TE': 'Trailers',
            'User-Agent': self.user_agent,
            'X-TimeZone-Id': 'America/Chicago'
        })

        resp = urlopen(req)
        resp_headers = resp.info()
        resp_body = gzip.decompress(resp.read()).decode('utf-8')

        self.log_cursor.execute("""
            INSERT INTO ConnectionLog
                (timestamp, url, request_headers, request_body, response_headers, response_body)
            VALUES
                (?, ?, ?, ?, ?, ?);
        """, (datetime.now(), req.get_full_url(), json.dumps(req.headers), str(req.data), str(resp_headers), str(resp_body)))
        self.log_db.commit()

        return json.loads(resp_body)

    def make_limit_sell(self, guid, price, quantity):
        host = "nummus.robinhood.com"
        filename = "/orders/"

        req_body = '{"account_id":"'+self.account+'","currency_pair_id":"'+guid+'","price":"'+str(price)+'","quantity":"'+str(quantity)+'","ref_id":"'+str(uuid4())+'","side":"sell","time_in_force":"gtc","type":"limit"}'

        req = Request('https://'+host+filename, headers={
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Length': str(len(req_body)),
            'Content-Type': 'application/json',
            'Authorization': self.token,
            'Connection': 'keep-alive',
            'Host': host,
            'Origin': 'https://robinhood.com',
            'Referer': 'https://robinhood.com',
            'TE': 'Trailers',
            'User-Agent': self.user_agent,
            'X-TimeZone-Id': 'America/Chicago'
        }, data=req_body.encode('utf-8'))
        resp = urlopen(req)
        resp_headers = str(resp.getheaders())
        resp_body = resp.read().decode('utf-8')

        if self.log_db:
            self.log_cursor.execute("""
                INSERT INTO ConnectionLog
                    (timestamp, url, request_headers, request_body, response_headers, response_body)
                VALUES
                    (?, ?, ?, ?, ?, ?);
            """, (datetime.now(), req.get_full_url(), json.dumps(req.headers), str(req.data), str(resp_headers), str(resp_body)))
            self.log_db.commit()

        return json.loads(resp_body)
    
    def make_limit_buy(self, guid, price, quantity):
        host = "nummus.robinhood.com"
        filename = "/orders/"

        req_body = '{"account_id":"'+self.account+'","currency_pair_id":"'+guid+'","price":"'+str(price)+'","quantity":"'+str(quantity)+'","ref_id":"'+str(uuid4())+'","side":"buy","time_in_force":"gtc","type":"limit"}'

        req = Request('https://'+host+filename, headers={
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Length': str(len(req_body)),
            'Content-Type': 'application/json',
            'Authorization': self.token,
            'Connection': 'keep-alive',
            'Host': host,
            'Origin': 'https://robinhood.com',
            'Referer': 'https://robinhood.com',
            'TE': 'Trailers',
            'User-Agent': self.user_agent,
            'X-TimeZone-Id': 'America/Chicago'
        }, data=req_body.encode('utf-8'))
        resp = urlopen(req)
        resp_headers = str(resp.getheaders())
        resp_body = resp.read().decode('utf-8')

        if self.log_db:
            self.log_cursor.execute("""
                INSERT INTO ConnectionLog
                    (timestamp, url, request_headers, request_body, response_headers, response_body)
                VALUES
                    (?, ?, ?, ?, ?, ?);
            """, (datetime.now(), req.get_full_url(), json.dumps(req.headers), str(req.data), str(resp_headers), str(resp_body)))
            self.log_db.commit()

        return json.loads(resp_body)
    
    def get_order(self, order_guid):
        host = "nummus.robinhood.com"
        filename = "/orders/"+order_guid+"/"

        req = Request('https://'+host+filename, headers={
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Type': 'application/json',
            'Authorization': self.token,
            'Connection': 'keep-alive',
            'Host': host,
            'Origin': 'https://robinhood.com',
            'Referer': 'https://robinhood.com',
            'TE': 'Trailers',
            'User-Agent': self.user_agent,
            'X-TimeZone-Id': 'America/Chicago'
        })

        resp = urlopen(req)
        resp_headers = str(resp.getheaders())
        resp_body = resp.read().decode('utf-8')

        if self.log_db:
            self.log_cursor.execute("""
                INSERT INTO ConnectionLog
                    (timestamp, url, request_headers, request_body, response_headers, response_body)
                VALUES
                    (?, ?, ?, ?, ?, ?);
            """, (datetime.now(), req.get_full_url(), json.dumps(req.headers), str(req.data), resp_headers, resp_body))
            self.log_db.commit()

        return json.loads(resp_body)
    
    def get_holdings(self):
        host = "nummus.robinhood.com"
        filename = "/holdings/"

        req = Request('https://'+host+filename, headers={
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Type': 'application/json',
            'Authorization': self.token,
            'Connection': 'keep-alive',
            'Host': host,
            'Origin': 'https://robinhood.com',
            'Referer': 'https://robinhood.com',
            'TE': 'Trailers',
            'User-Agent': self.user_agent,
            'X-TimeZone-Id': 'America/Chicago'
        })

        resp = urlopen(req)
        resp_headers = str(resp.getheaders())
        resp_body = resp.read().decode('utf-8')

        if self.log_db:
            self.log_cursor.execute("""
                INSERT INTO ConnectionLog
                    (timestamp, url, request_headers, request_body, response_headers, response_body)
                VALUES
                    (?, ?, ?, ?, ?, ?);
            """, (datetime.now(), req.get_full_url(), json.dumps(req.headers), str(req.data), resp_headers, resp_body))
            self.log_db.commit()

        return json.loads(resp_body)
    
    def get_currency_pairs(self):
        host = "nummus.robinhood.com"
        filename = "/currency_pairs/"

        req = Request('https://'+host+filename, headers={
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Type': 'application/json',
            'Authorization': self.token,
            'Connection': 'keep-alive',
            'Host': host,
            'Origin': 'https://robinhood.com',
            'Referer': 'https://robinhood.com',
            'TE': 'Trailers',
            'User-Agent': self.user_agent,
            'X-TimeZone-Id': 'America/Chicago'
        })

        resp = urlopen(req)
        resp_headers = str(resp.getheaders())
        resp_body = resp.read().decode('utf-8')

        if self.log_db:
            self.log_cursor.execute("""
                INSERT INTO ConnectionLog
                    (timestamp, url, request_headers, request_body, response_headers, response_body)
                VALUES
                    (?, ?, ?, ?, ?, ?);
            """, (datetime.now(), req.get_full_url(), json.dumps(req.headers), str(req.data), resp_headers, resp_body))
            self.log_db.commit()

        return json.loads(resp_body)