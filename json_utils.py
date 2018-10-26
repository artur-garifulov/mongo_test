# -*- coding: utf-8 -*-


def compare_json(expected_json, target_json):
    """Recursively compare keys of two json objects.

    Args:
        expected_json: expected json object.
        target_json: target json object.

    Returns:
        True if json objects keys are equal. False otherwise.
    """
    for key_ in expected_json:
        if type(expected_json[key_]) is dict:
            if key_ not in target_json or not compare_json(
                    expected_json[key_], target_json[key_]):
                return False
        else:
            if key_ not in target_json:
                return False
    return True
