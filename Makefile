# Uses xe.com currency data API: https://www.xe.com/xecurrencydata/
#
# Contains xe.com API credentials in 'user' and 'pass' variables:
#     user := <xe.com Account API ID>
#     pass := <xe.com Account API Key>
include credentials.mk

verbose :=
randmin := $(shell awk 'BEGIN{srand();printf("%d", 60*rand())}')

xebase := https://xecdapi.xe.com/v1/historic_rate/period/
xefrom := USD
xeto   := GBP,EUR,SGD
# Trial API access only gives access to 30 days of history
period := -30 days
today  := $(shell date --iso)
fado   := $(shell date -d'$(period)' --iso)
xeurl  := $(xebase)?from=$(xefrom)&to=$(xeto)&start_timestamp=$(fado)&end_timestamp=$(today)

xrurl := https://v6.exchangerate-api.com/v6/$(xrak)/latest/$(xefrom)
xrtoday := xr-$(today).json

xrates.json:
	curl -u '$(user):$(pass)' '$(xeurl)' | json_pp | tee $@

$(xrtoday):
ifeq "$(verbose)" "yes"
	curl '$(xrurl)' | json_pp | tee $@
else
	@curl -s '$(xrurl)' | json_pp > $@
endif

getxr: $(xrtoday)

rmxr:
	rm -f $(xrtoday)

atclean:
	@for j in $$(atq | awk '{print $$1}'); do \
		if at -c $$j | grep -qs '^make sked$$'; then \
			atrm $$j ;\
		fi ;\
	done

sked: getxr atclean
	echo 'make sked' | at -M 7:$(randmin)am tomorrow

retry: rmxr getxr

.PHONY: default
default:
	@echo No default

.PHONY: clean
clean:
	rm -f *~

.PHONY: pristine
pristine: clean
	rm -f xrates.json
