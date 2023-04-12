import attr
from typing import *


class Attrs(object):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    }


@attr.s(slots=True)
class ParseResult:
    name: Optional[str] = attr.ib(default=None)
    occupancy: Optional[str] = attr.ib(default=None)
    rating: Optional[float] = attr.ib(default=None)
    firm_id: Optional[str] = attr.ib(default=None)
    address: Optional[dict] = attr.ib(default=None)
    about: Optional[str] = attr.ib(default=None)
    phone_number: Optional[list] = attr.ib(default=None)
    social_medias: Optional[dict] = attr.ib(default=None)
    website: Optional[str] = attr.ib(default=None)
    mail: Optional[str] = attr.ib(default=None)

    def getSteep(self):
        return attr.asdict(self)

    def getFields(self):
        return attr.fields(self.__class__)
