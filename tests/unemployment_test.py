
# see also:
#  + https://github.com/prof-rossetti/codebase-cleanup-2021/pull/5/files
#  + https://github.com/prof-rossetti/intro-to-python/blob/e52b83da873584215d22e759b71b4fdf6b9cc9f2/notes/devtools/travis-ci.md
#  + https://github.com/prof-rossetti/intro-to-python/issues/103

import os
import pytest
import requests_mock


from app.unemployment import fetch_unemployment_data, ALPHAVANTAGE_API_KEY


#
# INTEGRATION TESTS (END TO END, may need to be skipped on CI)
#

@pytest.mark.skipif(os.getenv("CI")=="true", reason="avoid issuing HTTP requests on the CI server") # skips this test on CI
def test_fetch_data():

    data = fetch_unemployment_data()
    #breakpoint()

    # expecting the data to be a list of dictionaries
    assert isinstance(data, list)

    # expecting lots of months worth of data
    assert len(data) > 800

    # the latest month will change over time, so we maybe won't be able to test the exact values,
    # ... but we can test the structure (for example, the expected keys and their datatypes):

    latest_month = data[0] #> something like {'date': '2022-02-01', 'value': '3.8'}
    assert isinstance(latest_month, dict)
    assert sorted(list(latest_month.keys())) == ["date", "value"]

    assert isinstance(latest_month["date"], str)
    assert isinstance(latest_month["value"], str)


#
# UNIT TESTS (using mock data to avoid a network request, can be run on CI)
#
# see: https://requests-mock.readthedocs.io/en/latest/pytest.html


#
# MOCK DATA
#

mock_error_response = {
    "Error Message": "Invalid API call. Please retry or visit the documentation (https://www.alphavantage.co/documentation/) for TIME_SERIES_DAILY."
}

mock_rate_limit_response = {
    "Note": "Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls per minute and 500 calls per day. Please visit https://www.alphavantage.co/premium/ if you would like to target a higher API call frequency."
}

mock_unemployment_response = {
    "name": "Unemployment Rate",
    "interval": "monthly",
    "unit": "percent",
    "data": [
        {
            "date": "2022-02-01",
            "value": "3.8"
        },
        {
            "date": "2022-01-01",
            "value": "4.0"
        },
        {
            "date": "2021-12-01",
            "value": "3.9"
        }
    ]
} # this is an abbreviated version of the real response


def test_fetch_data_using_mock_responses():

    # this is the real URL that gets requested
    request_url = f"https://www.alphavantage.co/query?function=UNEMPLOYMENT&apikey={ALPHAVANTAGE_API_KEY}"


    # TEST 1
    # the function should work as expected when the request is successful:
    with requests_mock.mock() as mocker:
        # shortcut to override the request and return some specified mock data
        mocker.get(request_url, json=mock_unemployment_response)

        # now we test the function in question
        data = fetch_unemployment_data()
        #breakpoint()

        assert isinstance(data, list)
        assert len(data) == 3

        latest_month = data[0]
        assert latest_month == {'date': '2022-02-01', 'value': '3.8'}


    # TEST 2
    # the function should fail gracefully when encountering a rate limit error:
    with requests_mock.mock() as mocker:
        # shortcut to override the request and return some specified mock data
        mocker.get(request_url, json=mock_rate_limit_response)

        # now we test the function in question
        data = fetch_unemployment_data()
        assert data == None
