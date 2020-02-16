PY ?= $(shell pipenv --py)

OUTPUT = motogp.ics
SESSIONS = Race

calendar:
	env OUTPUT="$(OUTPUT)" SESSIONS="$(SESSIONS)" $(PY) motogp_calendar.py
