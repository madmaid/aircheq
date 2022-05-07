import re
import datetime
import collections
import itertools
import typing

import lxml.html
import requests
import dateutil.parser

from ... import userconfig
from . import model
from .base import GuideParser, ProgramDict
from ..utils import parse_time, naive_to_JST, datetime_hour_over_24


class Parser(GuideParser):
    def get_channels(self) -> dict[str, str]:
        """
        return dict {"channel": "channel_jp"}
        """
        return {"agqr": "超 A&G"}

    @staticmethod
    def __col(col):
        yield col
        while True:
            yield None


    @staticmethod
    def parse_boxed(table: lxml.html.HtmlElement) -> str:
        start = table.xpath(".//dt")[0].text
        desc = table.xpath(".//div/dd/a")[0].text
        return start + " " + desc

    @staticmethod
    def parse_description(program_elem: lxml.html.HtmlElement) -> str:
        xpath_base = ".//div[contains(@class, 'dailyProgram-itemDescription')]"

        xpath_root = xpath_base + "/text()"
        xpath_nested = xpath_base + "/div/text()"

        description = (
            "".join(program_elem.xpath(xpath_root)) +
            "\n".join(program_elem.xpath(xpath_nested))
        )
        return description.strip()

    def parse_guide(self, html: str, date: datetime.date) -> (
        typing.Generator[ProgramDict, None, None]
    ):
        # parse once per date
        root = lxml.html.fromstring(html)
        programs = root.xpath("//div[@class='block_contents_bg']/article")
        channel, channel_jp = tuple(self.get_channels().items())[0]

        for program in programs:
            times_str = program.xpath(".//h3")[0].text
            start_str, end_str = times_str.split("–")

            start_hour, start_minute = parse_time(start_str)
            start = datetime_hour_over_24(
                date, int(start_hour), int(start_minute))

            end_hour, end_minute = parse_time(end_str)
            end = datetime_hour_over_24(date, int(end_hour), int(end_minute))

            title_element = program.xpath(
                ".//p[@class='dailyProgram-itemTitle']")[0]
            title = title_element.xpath("./a")[0].text
            is_movie = len(title_element.xpath("./a/i")) > 0

            personarities = "".join(
                program.xpath(
                    ".//p[@class='dailyProgram-itemPersonality']/a/text()")
            )
            description = self.parse_description(program)
            guest = " ".join(
                    program.xpath(
                        ".//div[@class='dailyProgram-itemGuest']/text()")
            )
            boxed_programs = program.xpath(
                ".//dl[@class='dailyProgram-subTable']/div")
            boxed_info = "\n".join(self.parse_boxed(boxed)
                                   for boxed in boxed_programs
                                   )

            info = "\n".join((personarities, description, guest, boxed_info))

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

    def get_program(self, url: str, date: datetime.date) -> (
            typing.Generator[model.Program, None, None]
    ):
        req = requests.get(url)
        req.raise_for_status()

        try:
            programs = self.parse_guide(req.text, date)
        except Exception as e:
            raise e

        for program in programs:
            yield model.dict_to_program(program)

    def get_programs(self, url=None):
        if url is None:
            url = self.config["agqr"]["guide_url"]

        if url[-1] != '?':
            url += '?'

        now = datetime.datetime.now()
        if now.hour < 5:
            # workaround for 24:00-29:00
            now -= datetime.timedelta(days=1)
        available_dates = tuple(
            now.date() + datetime.timedelta(days=delta) for delta in range(7))

        for date in available_dates:
            date_query = 'date=' + date.strftime("%Y%m%d")
            try:
                yield from self.get_program(url + date_query, date)
            except Exception as e:
                raise e
