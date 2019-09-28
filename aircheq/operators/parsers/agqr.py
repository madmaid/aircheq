import re
import datetime
import collections
import itertools

import lxml.html
import requests

from ... import config
from . import model

from ..utils import naive_to_JST

def get_channels():
    """
    return dict {"channel": "channel_jp"}
    """
    return {"agqr": "超 A&G"}

def __col(col):
    yield col
    while True:
        yield None

def table_to_2ddict(table):
    result = collections.defaultdict(lambda: collections.defaultdict())
    for row_i, row in enumerate(table.xpath("./tr")):
        for col_i, col in enumerate(row.xpath('./td')):

            colspan = int(col.get('colspan', 1))
            rowspan = int(col.get('rowspan', 1))

            while row_i in result and col_i in result[row_i]:
                # skip span
                col_i += 1

            # fill

            # hoped to write following
            # for i in range_row:
            #   for j in range_col:
            #       result[i][j] = __col(col)
            # but generator works only at inner loop
            # itertools.product is instead of nested loop
            range_row = range(row_i, row_i + rowspan)
            range_col = range(col_i, col_i + colspan)
            for (i, j), cell in zip(itertools.product(range_row, range_col), __col(col)):
                result[i][j] = cell

    return result

def parse_guide(html):
    """
    html string => list contains program dict
    """
    # ! CAUTION !
    # following codes parse HTML designed with table-layout
    root = lxml.html.fromstring(html)
    this_year = datetime.date.today().year

    strptime = datetime.datetime.strptime
    _format = (lambda date_str:
            strptime(re.search("\d+/\d+", date_str).group(), "%m/%d").replace(year=this_year)
    )
    DATES = [_format(date).date() for date in root.xpath('//table/thead/tr/td/text()')]

    programs = []
    table = root.xpath('//table/tbody')[0]
    for row_i, row in sorted(table_to_2ddict(table).items()):
        for (col_i, cell), date in zip(sorted(row.items()), DATES):

            if cell is None:
                continue

            if cell.xpath('./div[@class="title-p"]/a'):
                title = "".join(cell.xpath('./div[@class="title-p"]/a/text()'))
            else:
                title = "".join(cell.xpath('./div[@class="title-p"]/text()')
                                ).replace("\n","")

            rowspan = int(cell.attrib['rowspan'])
            duration = datetime.timedelta(minutes=rowspan)



            str_time = cell.xpath('./div[@class="time"]')[0].text.replace("\n", "")
            str_hour, str_minute = re.search('(\d+):(\d+)', str_time).groups()
            if int(str_hour) > 23:
                hour = abs(int(str_hour) - 24)
                date += datetime.timedelta(days=1)
            else:
                hour = int(str_hour)
            time = datetime.time(hour, int(str_minute))



            get_href = (lambda elem, expr:
                    elem.xpath(expr)[0].attrib["href"] if elem.xpath(expr) != [] else ""
                )
            program_url = get_href(cell, './div[@class="title-p"]/a')
            mail_to = get_href(cell, './div[@class="rp"]/a')

            person = "".join(cell.xpath('./div[@class="rp"]/text()')).replace("\n", "")
            info = '\n'.join([person, program_url, mail_to])



            is_movie = bool(cell.xpath('./div[@class="time"]/span/img'))
            is_repeat = cell.attrib['class'] == 'bg-repeat'  # 'bg-l' or 'bg-f':




            start = naive_to_JST(datetime.datetime.combine(date, time))

            is_boxed = re.search("頃", str_time) is not None
            if is_boxed:
                # CAUTION:
                # if a boxed program strides over 0AM, this doesn't work correctly

                parent = tuple(p for p in programs if p["end"] == start)[-1] 

                boxed_info = "\n".join([start.isoformat(), title, info])

                programs[programs.index(parent)].update({
                        "info": parent["info"] + boxed_info,
                        "duration": parent["duration"] + duration,
                        'end': parent['end'] + duration,
                    })
            else:
                channel, channel_jp = tuple(get_channels().items())[0]
                programs.append({
                        'service': 'agqr',
                        'channel': channel,
                        'channel_jp': channel_jp,
                        'title': title,
                        'start': start,
                        'end': start + duration,
                        'duration': duration,
                        'info': info,
                        # "casts": person,
                        'is_repeat': is_repeat,
                        'is_movie': is_movie,
                })
    return programs

def get_programs(url=config.AGQR_GUIDE_URL):
    req = requests.get(url)
    req.raise_for_status()

    for dic in parse_guide(req.content):
        yield model.dict_to_program(dic)

