# -*- coding: utf-8 -*-
from mongoengine import *
import enum
import json
import random
import unittest

import queries
import json_utils


class ImagesEnum(enum.Enum):
    cover = 'cover'
    background = 'background'
    foreground = 'foreground'


class QualityEnum(enum.IntEnum):
    LD = 0
    SD = 1
    HD = 2
    FULL_HD = 3


class File(EmbeddedDocument):
    path = StringField()
    quality = IntField()


class Quote(EmbeddedDocument):
    source = StringField()
    text = StringField()


class Episode(EmbeddedDocument):
    num = IntField()
    alias = StringField()
    files = EmbeddedDocumentListField('File')


class Season(Document):
    num = IntField()
    alias = StringField()
    episodes = EmbeddedDocumentListField('Episode', db_field='items')
    meta = {
        'collection': 'products',
        'allow_inheritance': True
    }


class Series(Document):
    title = StringField()
    alias = StringField()
    description = StringField()
    seasons = ListField(ReferenceField('Season'), db_field='items')
    quote = EmbeddedDocumentField('Quote')
    images = MapField(URLField())
    meta = {
        'collection': 'products',
        'allow_inheritance': True
    }


class TestTask(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        connect('test', host="mongo")

    def test_01_create_documents(self):
        def __quote(i):
            source = 'QuoteSource %i' % i
            return {'source': source, 'text': 'test quote'}

        def __images(i):
            return {img.value: 'image path %i' % i for img in ImagesEnum}

        def __files():
            files = list()
            for i in QualityEnum:
                f = File(quality=i, path='file path %i' % i)
                files.append(f)
            return files

        def __episodes():
            episodes = list()
            for i in range(0, random.randint(1, 30)):
                s = Episode(num=i, alias='episode%i' % i, files=__files())
                episodes.append(s)
            return episodes

        def __seasons():
            seasons = list()
            for i in range(0, random.randint(1, 10)):
                s = Season(num=i, alias='season%i' % i, episodes=__episodes())
                s.save()
                seasons.append(s)
            return seasons

        def __series():
            series = list()
            for i in range(0, random.randint(1, 10)):
                s = Series.objects(
                    title='series %i' % i,
                    alias='series%i' % i
                    ).modify(
                        upsert=True,
                        new=True,
                        set__quote=__quote(i),
                        set__images=__images(i),
                        set__description='description %i' % i,
                        set__seasons=__seasons())
                series.append(s)
            return series
        self.assertTrue(__series())

    def test_02_get_series(self):
        """Check structure of result of get_series method."""

        expected_response = """
        {
          "path": "/series/series4",
          "slide": {
            "background": "image path 4",
            "foreground": "image path 4"
          },
          "title": "series 4",
          "description": "description 4",
          "cover": "image path 4",
          "quote": "test quote",
          "quote_source": "QuoteSource 4",
          "seasons": [
            {
              "path": "/series/series4/season0",
              "title": "0 сезон",
              "episodes": [
                {
                  "path": "/series/series4/season0/episode0",
                  "title": "Эпизод 0 сезона",
                  "files": [
                    {
                      "path": "file path 0",
                      "label": "LD",
                      "quality": 0
                    }
                  ]
                }
              ]
            }
          ]
        }
        """
        target_json = queries.get_series()

        # Compare structure of two json objects
        self.assertTrue(json_utils.compare_json(json.loads(expected_response),
                                                target_json))


if __name__ == '__main__':
    unittest.main()
