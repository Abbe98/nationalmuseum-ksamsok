def resolve_license(license):
    if license == 'CC BY SA':
        return ['http://kulturarvsdata.se/resurser/license#by-sa', 'http://creativecommons.org/licenses/by-sa/4.0/']
    if license == 'Public Domain':
        ['http://kulturarvsdata.se/resurser/license#pdmark', 'http://creativecommons.org/publicdomain/mark/1.0/']

    return ['http://kulturarvsdata.se/resurser/license#inc', 'http://rightsstatements.org/vocab/InC/1.0/']
