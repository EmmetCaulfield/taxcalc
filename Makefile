include credentials.mk

xebase := https://xecdapi.xe.com/v1/historic_rate/period/
xefrom := USD
xeto   := GBP,EUR,SGD
period := -30 days
today  := $(shell date --iso)
fado   := $(shell date -d'$(period)' --iso)
xeurl  := $(xebase)?from=$(xefrom)&to=$(xeto)&start_timestamp=$(fado)&end_timestamp=$(today)

xrates.json:
	curl -u '$(user):$(pass)' '$(xeurl)' | json_pp | tee $@

.PHONY: default
default:
	@echo No default

.PHONY: clean
clean:
	rm -f *~

.PHONY: pristine
pristine: clean
	rm -f xrates.json
