# RHPyLib

Author: Andrew Madden \<andrewsmadden@gmail.com>

## Overview
RHPyLib is a very basic module for connecting to the Robinhood Web API for cryptocurrency trading. This allows developers to progamatically make calls to Robinhood's services.

## Limitations
Currently the library only supports cryptocurrency, does not support creating market orders, and cannot pull a user's holdings. I would like to alleviate this in future versions.

I would also like to add some sort of indexing/search feature in order to look for a stock without knowing its guid representation.

## Importing RHPyLib

Currently the library is not available via pip. In order to use the library for now, place the rhpylib folder into the working directory where you will run your script. From there, you can import the library as such:

```py
from rhpylib.api import RHConnection
```

### Getting Started

In order to create a connection to Robinhood, you'll need either an existing OAuth2 token, or a set of credentials (username/email, password, and mfa token if applicable)

You can create a connection like this:
```py
conn = RHConnection(token="Bearer <long_token_string>")
```

or like this:

```py
conn = RHConnection(un="<username>", pw="<password>", mfa="<mfa token from otp authentication app/tool>")
```

### Getting Quotes

You can get an up to date quote for a stock or cryptocurrency using get_quote and providing the guid of the stock or cryptocurrency.

```py
# Get a quote for the current price of DOGE. guid='1ef78e1b-049b-4f12-90e5-555dcf2fe204'
quote = conn.get_quote_crypto('1ef78e1b-049b-4f12-90e5-555dcf2fe204')

# quote = {
#   "ask_price": <float>,
#   "bid_price": <float>,
#   "mark_price": <float>,
#   "high_price": <float>,
#   "low_price": <float>,
#   "open_price": <float>,
#   "symbol": <string>,
#   "id": "1ef78e1b-049b-4f12-90e5-555dcf2fe204",
#   "volume": <float>
# }
```

### Historical Data

You can get the historical data for a given stock or cryptocurrency as well by providing the guid of the stock.

```py
# Get the last hour of historical data for ETC at 15 second intervals. guid="7b577ce3-489d-4269-9408-796a0d1abb3a"
# the last three arguments vary the time for the historical data:
#   '24_7', '15second', 'hour' => The last hour of historical data at 15 second intervals
#   '24_7', 'hour', 'week' => The last week of historical data at 1 hour intervals
data = conn.get_historical_data("7b577ce3-489d-4269-9408-796a0d1abb3a", '24_7', '15second', 'hour')['data_points']
```

### Making orders

You can create limit buy orders:
```py
# Create limit buy for 200 ETC with a limit of $7.50
order = conn.make_limit_buy_crypto("7b577ce3-489d-4269-9408-796a0d1abb3a", 7.5, 200)
```
You can create limit sell orders:
```py
# Create limit sell for 200 ETC with a limit of $7.50
order = conn.make_limit_sell_crypto("7b577ce3-489d-4269-9408-796a0d1abb3a", 7.5, 200)
```
You can check your the status of your order after you've placed it:
```py
order_id = conn.make_limit_sell_crypto("7b577ce3-489d-4269-9408-796a0d1abb3a", 7.5, 200)['id']

# Wait some amount of time, unless you're lucky

status = conn.get_order(order_id)['state']

# If status is "filled", that means your order completed!
```

### Finding guids for stocks/crypto

You can use the query_market method to search for different stocks or cryptocurrencies. Each search returns a dictionary object with keys of "instruments", "currency_pairs", 

To search for stocks:
```py
stocks = conn.query_market('AMD')['instruments']
```

To search for crypto:
```py
crypto = conn.query_market("ETC")['currency_pairs']
```