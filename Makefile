# Uses xe.com currency data API: https://www.xe.com/xecurrencydata/
#
# Contains xe.com API credentials in 'user' and 'pass' variables:
#     user := <xe.com Account API ID>
#     pass := <xe.com Account API Key>
include credentials.mk

xebase := https://xecdapi.xe.com/v1/historic_rate/period/
xefrom := USD
xeto   := GBP,EUR,SGD
# Trial API access only gives access to 30 days of history
period := -30 days
today  := $(shell date --iso)
fado   := $(shell date -d'$(period)' --iso)
xeurl  := $(xebase)?from=$(xefrom)&to=$(xeto)&start_timestamp=$(fado)&end_timestamp=$(today)

xrurl := https://v6.exchangerate-api.com/v6/$(xrak)/latest/$(xefrom)

xrates.json:
	curl -u '$(user):$(pass)' '$(xeurl)' | json_pp | tee $@

xr-$(today).json:
	curl '$(xrurl)' | json_pp | tee $@

getxr: xr-$(today).json

.PHONY: default
default:
	@echo No default

.PHONY: clean
clean:
	rm -f xr-api.json *~

.PHONY: pristine
pristine: clean
	rm -f xrates.json
