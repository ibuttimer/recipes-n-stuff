#  MIT License
#
#  Copyright (c) 2023 Ian Buttimer
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM,OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
from pathlib import Path
from utils import append_slash, url_path

# name of this app
THIS_APP = Path(__file__).resolve().parent.name

# common field names
COUNTRY_FIELD = "country"
SUBDIVISION_FIELD = "subdivision"
USER_FIELD = "user"
STREET_FIELD = "street"
STREET2_FIELD = "street2"
CITY_FIELD = "city"
STATE_FIELD = "state"
POSTCODE_FIELD = "postcode"
IS_DEFAULT_FIELD = "is_default"

# Address routes related
PK_PARAM_NAME = "pk"
ADDRESSES_URL = "addresses"
ADDRESS_NEW_URL = url_path(ADDRESSES_URL, "new")
ADDRESS_ID_URL = url_path(ADDRESSES_URL, f"<int:{PK_PARAM_NAME}>")
ADDRESSES_ID_DEFAULT_URL = \
    url_path(ADDRESSES_URL, f"<int:{PK_PARAM_NAME}>", "default")

# convention is addresses route names begin with 'address'
ADDRESSES_ROUTE_NAME = "addresses"
ADDRESS_NEW_ROUTE_NAME = "address_new"
ADDRESS_ID_ROUTE_NAME = "address_id"
ADDRESSES_ID_DEFAULT_ROUTE_NAME = "address_id_default"

# CountryInfo routes related
COUNTRYINFO_URL = "countryinfo"
COUNTRYINFO_CODE_URL = url_path(COUNTRYINFO_URL, "<str:country>")

# convention is CountryInfo route names begin with 'address'
COUNTRYINFO_ROUTE_NAME = "countryinfo"
COUNTRYINFO_CODE_ROUTE_NAME = "countryinfo_country"

# context
ADDRESS_FORM_CTX = 'address_form'
ADDRESS_LIST_CTX = 'address_list'
NEW_ENTRY_CTX = 'new_entry'
COUNT_CTX = 'count'
