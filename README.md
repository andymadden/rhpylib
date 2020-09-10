# RHPyLib

Author: Andrew Madden \<andrewsmadden@gmail.com>

## Overview
RHPyLib is a very basic module for connecting to the Robinhood Web API. This allows developers to progamatically make calls to Robinhood's services.

## Limitations
Currently the library does not support creating limit orders and cannot pull a user's holdings. I would like to alleviate this in future versions.

## Importing RHPyLib

Currently the library is not available via pip. In order to use the library for now, place the rhpylib folder into the working directory where you will run your script. From there, you can import the library as such:

```py
from rhpylib.api import RHConnection
```

### Getting Started

In order to create a connection to Robinhood, you'll need either an existing OAuth2 token, or a set of credentials (username/email, password, and mfa token if applicable)

