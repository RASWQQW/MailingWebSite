import asyncio
import os
import pathlib
import re

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


plop = {'about': 'Кафе',
  'address': {'city': 'Туркестан\xa0м-н, Алатауский район, '
                      'Алматы, 050047/A01C3H5',
              'floor': '1 этаж',
              'street': {'link': '/almaty/geo/9430047375010954',
                         'text': 'Микрорайон Туркестан,\xa0'
                                 '76в'}},
  'firm_id': 'https://2gis.kz/almaty/firm/70000001066506546',
  'mail': None,
  'name': 'Достар\xa0',
  'occupancy': 'Кафе',
  'phone_number': 'tel:+77077585358',
  'rating': 4.6,
  'social_medias': {'Instagram': 'https://instagram.com/cafe__dostar',
                    'WhatsApp': 'https://wa.me/77077585358?text=%D0%97%D0%B4%D1%80%D0%B0%D0%B2%D1%81%D1%82%D0%B2%D1%83%D0%B9%D1%82%D0%B5!%0A%0A%D0%9F%D0%B8%D1%88%D1%83%20%D0%B8%D0%B7%20%D0%BF%D1%80%D0%B8%D0%BB%D0%BE%D0%B6%D0%B5%D0%BD%D0%B8%D1%8F%202%D0%93%D0%98%D0%A1.%0A%0A'},
  'website': 'https://instagram.com/cafe__dostar'}


# from api.execs.requesting import RequestSender as rr
#
# value = {plop.__setitem__(key, await rr().Deleter(value)) for key, value in plop.items()}
# print(plop)

