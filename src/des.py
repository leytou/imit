#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pyDes import des, ECB, PAD_PKCS5
import base64

secret_key = ':M)g>0C9'


def DesEncrypt(s):
    iv = secret_key
    k = des(secret_key, ECB, iv, pad=None, padmode=PAD_PKCS5)
    en = k.encrypt(s.encode('utf-8'), padmode=PAD_PKCS5)
    return str(base64.b64encode(en), 'utf-8')


def DesDecrypt(s):
    iv = secret_key
    k = des(secret_key, ECB, iv, pad=None, padmode=PAD_PKCS5)
    de = k.decrypt(base64.b64decode(s), padmode=PAD_PKCS5)
    return str(de, 'utf-8')
