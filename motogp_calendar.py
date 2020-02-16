#/usr/env/bin python
import os

from datetime import datetime, timedelta

from ics import AudioAlarm, Calendar, Event
from pyquery import PyQuery as pq


MOTOGP_CAL_URL = 'https://www.motogp.com/en/calendar'
TIME_FMT = '%Y-%m-%dT%H:%M:%S%z'


def _flag(code):
    '''
    Unicode Flags in Python

      See: http://schinckel.net/2015/10/29/unicode-flags-in-python/
    '''
    offset = 127397
    return chr(ord(code[0]) + offset) + chr(ord(code[1]) + offset)


_FLAGS = {
    'ARGENTINA': _flag('AR'),
    'AUSTRALIA': _flag('AU'),
    'AUSTRIA': _flag('AT'),
    'CZECH REPUBLIC': _flag('CZ'),
    'FINLAND': _flag('FI'),
    'FRANCE': _flag('FR'),
    'GERMANY': _flag('DE'),
    'GREAT BRITAIN': _flag('GB'),
    'ITALY': _flag('IT'),
    'JAPAN': _flag('JP'),
    'MALAYSIA': _flag('MY'),
    'NETHERLANDS': _flag('NL'),
    'QATAR': _flag('QA'),
    'SPAIN': _flag('ES'),
    'THAILAND': _flag('TH'),
    'UNITED STATES': _flag('US'),
}


def resolve_event(evt_html):
    title = evt_html('.event_title a').text()
    if title.endswith('Test'):
        return None

    evt = Event(
        name=(
            f'MotoGP {_FLAGS[evt_html(".location span").eq(1).text()]} '
            f'{title} ({os.environ["SESSIONS"]})'),
        location=evt_html('.location span').eq(0).text(),
        url=f'{evt_html(".event_title a").attr("href")}#schedule')

    desc = []
    begin = None
    end = None
    sched_html = pq(url=evt.url, encoding='utf-8')
    for e in sched_html('.c-schedule__table-row').items():
        sessions = e('.c-schedule__table-cell:nth-child(3) span.hidden-xs').text()
        if not sessions.startswith(os.environ['SESSIONS']):
            continue

        category = e('.c-schedule__table-cell').eq(1).text().strip()
        ini_time = e('.c-schedule__time span').eq(0).attr('data-ini-time')
        if begin is None:
            begin = ini_time
        else:
            end = ini_time

        desc.append(f'{ini_time} {category} {sessions}')

    td = datetime.strptime(end, TIME_FMT) - datetime.strptime(begin, TIME_FMT)
    evt.begin = begin
    evt.description = '\n'.join(desc)
    evt.duration = timedelta(seconds=td.seconds + 7200)

    print(
        f'{evt.name}\n'
        f'Circuit: {evt.location}\n'
        f'Schedule:\n{evt.description}\n{"-" * 46}')

    return evt


if __name__ == '__main__':
    cal = Calendar()
    alarms = [AudioAlarm(trigger=timedelta(minutes=-30)),]

    cal_html = pq(url=MOTOGP_CAL_URL, encoding='utf-8')
    for e in cal_html('div.calendar_events div.event_container div.event').items():
        evt = resolve_event(e)

        if evt is None:
            continue

        evt.alarms = alarms
        cal.events.add(evt)

    with open(os.environ['OUTPUT'], 'w') as f:
        f.writelines(cal)
