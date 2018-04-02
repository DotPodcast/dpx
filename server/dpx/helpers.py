from base64 import b64encode
from hashlib import md5
from os import path
import random
import string


def create_slug(queryset, new, name=None, max_length=100):
    from django.template.defaultfilters import slugify
    from django.utils.timezone import now
    from hashlib import md5

    if name:
        base = slugify(name).replace('-', '')
    else:
        base = None

    if not base:
        slug = md5(now().isoformat().encode('utf-8')).hexdigest()
    else:
        slug = base[:max_length]

    if new:
        i = 1

        while queryset.filter(slug=slug).exists():
            rem = (max_length - 1) - len(str(i))
            slug = '%s-%d' % (base[:rem], i)
            i += 1

    return slug


def create_keypair():
    from os import chmod
    from Crypto.PublicKey import RSA

    key = RSA.generate(2048)
    return (
        pubkey.exportKey('OpenSSH'),
        key.exportKey('PEM')
    )


def create_token(length, include_punctuation=False):
    characters = ''

    while len(characters) < length:
        characters += string.digits + string.ascii_letters

        if include_punctuation:
            characters += string.punctuation

    return b64encode(
        ''.join(
            random.sample(characters, length)
        ).encode('utf-8')
    ).decode('utf-8')
