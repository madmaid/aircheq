import re
import datetime
import collections
import itertools

import lxml.html
import requests
import dateutil.parser

from ... import userconfig
from . import model

from ..utils import parse_time, naive_to_JST, datetime_hour_over_24

config = userconfig.TomlLoader()
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

def parse_old_guide(html: str) -> dict:
    """
    html string => list contains program dict
    """
    # ! CAUTION !
    # following codes parse HTML designed with table-layout
    root = lxml.html.fromstring(html)
    this_year = datetime.date.today().year

    parse_time = dateutil.parser.parse
    _format = (lambda date_str:
            parse_time(re.search("\d+/\d+", date_str).group()).replace(year=this_year)
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

def get_programs_from_old_guide(url=None):
    if url is None:
        url = config["agqr"]["guide_url"]
    req = requests.get(url)
    req.raise_for_status()


    for dic in parse_guide(req.content):
        yield model.dict_to_program(dic)

def parse_boxed(table: lxml.html.HtmlElement) -> str:
    start = table.xpath(".//dt")[0].text
    desc = table.xpath(".//div/dd/a")[0].text
    return start + " " + desc

def parse_guide(html, date):

    # parse once per date
    root = lxml.html.fromstring(html)
    programs = root.xpath("//div[@class='block_contents_bg']/article")
    channel, channel_jp = tuple(get_channels().items())[0]

    for program in programs:
        times_str = program.xpath(".//h3")[0].text
        start_str, end_str = times_str.split("–")

        start_hour, start_minute = parse_time(start_str)
        start = datetime_hour_over_24(date, int(start_hour), int(start_minute))

        end_hour, end_minute = parse_time(end_str)
        end = datetime_hour_over_24(date, int(end_hour), int(end_minute))

        title_element = program.xpath(".//p[@class='dailyProgram-itemTitle']")[0]
        title = title_element.xpath("./a")[0].text
        is_movie = len(title_element.xpath("./a/i")) > 0

        personarities = "".join(
                program.xpath(".//p[@class='dailyProgram-itemPersonality']/a/text()")
        )
        description = "".join(
                program.xpath(".//div[@class='dailyProgram-itemDescription']/text()")
        )
        guest = "".join(
                program.xpath(".//div[@class='dailyProgram-itemGuest']/text()")
        )
        boxed_programs = program.xpath(".//dl[@class='dailyProgram-subTable']/div")
        boxed_info  = "\n".join( parse_boxed(boxed) for boxed in boxed_programs )

        info = "\n".join(( personarities, description, guest, boxed_info))

        is_repeat = "is-repeat" in program.attrib["class"]

        yield {
                'service': 'agqr',
                'channel': channel,
                'channel_jp': channel_jp,
                'title': title,
                'start': naive_to_JST(start),
                'end': naive_to_JST(end),
                'duration': end - start,
                'info': info,
                # "casts": person,
                'is_repeat': is_repeat,
                'is_movie': is_movie,
        }



def get_program(url, date):
    req = requests.get(url)
    req.raise_for_status()

    try:
        programs = parse_guide(req.text, date)
    except Exception as e:
        raise e

    for program in programs:
        yield model.dict_to_program(program)

def get_programs(url=None):
    if url is None:
        url = config["agqr"]["guide_url"]

    if url[-1] != '?':
        url += '?'

    now = datetime.datetime.now()
    if now.hour < 5:
        # workaround for 24:00-29:00
        now -= datetime.timedelta(days=1)
    available_dates = tuple( now.date() + datetime.timedelta(days=delta) for delta in range(7) )

    for date in available_dates:
        date_query = 'date=' + date.strftime("%Y%m%d")
        try:
            yield from get_program(url + date_query, date)
        except Exception as e:
            raise e

