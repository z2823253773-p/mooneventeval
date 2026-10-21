"""Independent exact seconds-space oracle: Decimal text -> Fraction arithmetic."""
from decimal import Decimal
from fractions import Fraction


def number(text):
    return Fraction(Decimal(text))


def decimal_text(value):
    value = Fraction(value)
    numerator, denominator = value.numerator, value.denominator
    twos = fives = 0
    while denominator % 2 == 0:
        denominator //= 2; twos += 1
    while denominator % 5 == 0:
        denominator //= 5; fives += 1
    if denominator != 1:
        raise ValueError('non-terminating decimal')
    digits = max(twos, fives)
    scaled = abs(numerator) * 2**(digits-twos) * 5**(digits-fives)
    whole, fraction = divmod(scaled, 10**digits)
    tail = ('.' + str(fraction).zfill(digits).rstrip('0')) if fraction else ''
    return ('-' if numerator < 0 else '') + str(whole) + tail


def eligible(reference: dict, prediction: dict, config: dict) -> dict:
    collar = number(config.get('collar_s', '0.2'))
    ratio = number(config.get('offset_ratio', '0.5'))
    onset = number(prediction['onset_s']) - number(reference['onset_s'])
    offset = number(prediction['offset_s']) - number(reference['offset_s'])
    duration = number(reference['offset_s']) - number(reference['onset_s'])
    limit = max(collar, duration * ratio)
    label = reference['label'] == prediction['label']
    onset_pass, offset_pass = abs(onset) <= collar, abs(offset) <= limit
    return dict(label_match=label, onset_pass=onset_pass, offset_pass=offset_pass,
                eligible=label and onset_pass and offset_pass,
                onset_delta_s=decimal_text(onset), offset_delta_s=decimal_text(offset),
                onset_limit_s=decimal_text(collar), offset_limit_s=decimal_text(limit))
