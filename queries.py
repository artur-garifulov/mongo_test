# -*- coding: utf-8 -*-
from pymongo import MongoClient


client = MongoClient("mongo", 27017)
db = client.test


def get_series():
    """Receive series.

    Returns:
        Receive information about series.
    """
    query_result = db.products.aggregate([
        {"$lookup": {
            "from": "products",
            "localField": "items",
            "foreignField": "_id",
            "as": "seasons"
        }},
        {"$match": {
            "_cls": "Series"
        }},
        {"$project": {
            "document": "$$ROOT",
            "seasons": 1
        }},


        {"$addFields": {
            "path": {"$concat": ["/series/", "$document.alias"]},
            "slide.background": "$document.images.background",
            "slide.foreground": "$document.images.foreground",
        }},

        {"$project": {
            "document": 1,
            "title": "$document.title",
            "description": "$document.description",
            "path": 1,
            "cover": "$document.images.cover",
            "quote": "$document.quote.text",
            "quote_source": "$document.quote.source",
            "slide": 1,
            "seasons": {
                "$map": {
                    "input": "$seasons",
                    "as": "s",
                    "in": {
                        "path": {"$concat": ["$path", "/", "$$s.alias"]},
                        "title": {"$concat": [{"$toString": "$$s.num"}, " сезон"]},
                        "episodes": {
                            "$map": {
                                "input": "$$s.items",
                                "as": "e",
                                "in": {
                                    "path": {"$concat": ["$path", "/", "$$s.alias", "/", "$$e.alias"]},
                                    "title": {"$concat": ["Эпизод ", {"$toString": "$$e.num"}, " сезона"]},
                                    "files": {
                                        "$map": {
                                            "input": "$$e.files",
                                            "as": "f",
                                            "in": {
                                                "path": "$$f.path",
                                                "label": {
                                                    "$switch": {
                                                        "branches": [
                                                            {"case": {"$eq": ["$$f.quality", 0]}, "then": "LD"},
                                                            {"case": {"$eq": ["$$f.quality", 1]}, "then": "SD"},
                                                            {"case": {"$eq": ["$$f.quality", 2]}, "then": "HD"},
                                                            {"case": {"$eq": ["$$f.quality", 3]}, "then": "FULL_HD"},
                                                        ]
                                                    }
                                                },
                                                "quality": "$$f.quality"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
        }},

        {"$project": {
            "document": 0,
            "_id": 0
        }},
        {"$limit": 1}

    ])
    return next(query_result, [])
