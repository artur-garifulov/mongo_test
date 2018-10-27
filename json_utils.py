# -*- coding: utf-8 -*-


def compare_json(expected_json, target_json):
    """Recursively compare keys of two json objects.

    Args:
        expected_json: expected json object.
        target_json: target json object.

    Returns:
        True if json objects keys are equal. False otherwise.
    """
    if type(expected_json) is dict:
        for key_ in expected_json:
            if key_ not in target_json or not compare_json(
                    expected_json[key_], target_json[key_]):
                return False
    elif type(expected_json) is list:
        for exp_item, target_item in zip(expected_json, target_json):
            if not compare_json(exp_item, target_item):
                return False
    return True
