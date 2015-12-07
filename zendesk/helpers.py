import functools
import pickle

from apiclient import discovery
from flask import request
from httplib2 import Http
from oauth2client.client import Storage

from . import app, redis


def login_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if request.form.get('token') != app.config['API_TOKEN']:
            return {'error': 'Invalid API token.'}, 401
        return f(*args, **kwargs)
    return wrapper


def api_route(self, *args, **kwargs):
    def wrapper(cls):
        self.add_resource(cls, *args, **kwargs)
        return cls
    return wrapper


class RedisStorage(Storage):
    def __init__(self, instance, key, prefix='oauth2_'):
        self.instance = instance
        self.key = key
        self.prefix = prefix

    def locked_get(self):
        key = '%s%s' % (self.prefix, self.key)
        return pickle.loads(self.instance.get(key))

    def locked_put(self, credentials):
        key = '%s%s' % (self.prefix, self.key)
        self.instance.set(key, pickle.dumps(credentials))

    def locked_delete(self):
        key = '%s%s' % (self.prefix, self.key)
        self.instance.delete(key)


def build_service_from_id(profile_id):
    store = RedisStorage(redis, profile_id)
    credentials = store.get()
    http = credentials.authorize(Http())
    service = discovery.build('calendar', 'v3', http=http)

    return service


def fields_to_dict(data):
    """
    Takes list of structure [{'id': someid, 'value': somevalue}, ...].
    Returns {someid: someval, anotherid: anotherval}.
    """
    return {el['id']: el['value'] for el in data}


TZ_MAPPING = {
    'Abu Dhabi': 'Asia/Muscat',
    'Adelaide': 'Australia/Adelaide',
    'Alaska': 'America/Juneau',
    'Almaty': 'Asia/Almaty',
    'American Samoa': 'Pacific/Pago_Pago',
    'Amsterdam': 'Europe/Amsterdam',
    'Arizona': 'America/Phoenix',
    'Astana': 'Asia/Dhaka',
    'Athens': 'Europe/Athens',
    'Atlantic Time (Canada)': 'America/Halifax',
    'Auckland': 'Pacific/Auckland',
    'Azores': 'Atlantic/Azores',
    'Baghdad': 'Asia/Baghdad',
    'Baku': 'Asia/Baku',
    'Bangkok': 'Asia/Bangkok',
    'Beijing': 'Asia/Shanghai',
    'Belgrade': 'Europe/Belgrade',
    'Berlin': 'Europe/Berlin',
    'Bern': 'Europe/Berlin',
    'Bogota': 'America/Bogota',
    'Brasilia': 'America/Sao_Paulo',
    'Bratislava': 'Europe/Bratislava',
    'Brisbane': 'Australia/Brisbane',
    'Brussels': 'Europe/Brussels',
    'Bucharest': 'Europe/Bucharest',
    'Budapest': 'Europe/Budapest',
    'Buenos Aires': 'America/Argentina/Buenos_Aires',
    'Cairo': 'Africa/Cairo',
    'Canberra': 'Australia/Melbourne',
    'Cape Verde Is.': 'Atlantic/Cape_Verde',
    'Caracas': 'America/Caracas',
    'Casablanca': 'Africa/Casablanca',
    'Central America': 'America/Guatemala',
    'Central Time (US & Canada)': 'America/Chicago',
    'Chatham Is.': 'Pacific/Chatham',
    'Chennai': 'Asia/Kolkata',
    'Chihuahua': 'America/Chihuahua',
    'Chongqing': 'Asia/Chongqing',
    'Copenhagen': 'Europe/Copenhagen',
    'Darwin': 'Australia/Darwin',
    'Dhaka': 'Asia/Dhaka',
    'Dublin': 'Europe/Dublin',
    'Eastern Time (US & Canada)': 'America/New_York',
    'Edinburgh': 'Europe/London',
    'Ekaterinburg': 'Asia/Yekaterinburg',
    'Fiji': 'Pacific/Fiji',
    'Georgetown': 'America/Guyana',
    'Greenland': 'America/Godthab',
    'Guadalajara': 'America/Mexico_City',
    'Guam': 'Pacific/Guam',
    'Hanoi': 'Asia/Bangkok',
    'Harare': 'Africa/Harare',
    'Hawaii': 'Pacific/Honolulu',
    'Helsinki': 'Europe/Helsinki',
    'Hobart': 'Australia/Hobart',
    'Hong Kong': 'Asia/Hong_Kong',
    'Indiana (East)': 'America/Indiana/Indianapolis',
    'International Date Line West': 'Pacific/Midway',
    'Irkutsk': 'Asia/Irkutsk',
    'Islamabad': 'Asia/Karachi',
    'Istanbul': 'Europe/Istanbul',
    'Jakarta': 'Asia/Jakarta',
    'Jerusalem': 'Asia/Jerusalem',
    'Kabul': 'Asia/Kabul',
    'Kaliningrad': 'Europe/Kaliningrad',
    'Kamchatka': 'Asia/Kamchatka',
    'Karachi': 'Asia/Karachi',
    'Kathmandu': 'Asia/Kathmandu',
    'Kolkata': 'Asia/Kolkata',
    'Krasnoyarsk': 'Asia/Krasnoyarsk',
    'Kuala Lumpur': 'Asia/Kuala_Lumpur',
    'Kuwait': 'Asia/Kuwait',
    'Kyiv': 'Europe/Kiev',
    'La Paz': 'America/La_Paz',
    'Lima': 'America/Lima',
    'Lisbon': 'Europe/Lisbon',
    'Ljubljana': 'Europe/Ljubljana',
    'London': 'Europe/London',
    'Madrid': 'Europe/Madrid',
    'Magadan': 'Asia/Magadan',
    'Marshall Is.': 'Pacific/Majuro',
    'Mazatlan': 'America/Mazatlan',
    'Melbourne': 'Australia/Melbourne',
    'Mexico City': 'America/Mexico_City',
    'Mid-Atlantic': 'Atlantic/South_Georgia',
    'Midway Island': 'Pacific/Midway',
    'Minsk': 'Europe/Minsk',
    'Monrovia': 'Africa/Monrovia',
    'Monterrey': 'America/Monterrey',
    'Montevideo': 'America/Montevideo',
    'Moscow': 'Europe/Moscow',
    'Mountain Time (US & Canada)': 'America/Denver',
    'Mumbai': 'Asia/Kolkata',
    'Muscat': 'Asia/Muscat',
    'Nairobi': 'Africa/Nairobi',
    'New Caledonia': 'Pacific/Noumea',
    'New Delhi': 'Asia/Kolkata',
    'Newfoundland': 'America/St_Johns',
    'Novosibirsk': 'Asia/Novosibirsk',
    "Nuku'alofa": 'Pacific/Tongatapu',
    'Osaka': 'Asia/Tokyo',
    'Pacific Time (US & Canada)': 'America/Los_Angeles',
    'Paris': 'Europe/Paris',
    'Perth': 'Australia/Perth',
    'Port Moresby': 'Pacific/Port_Moresby',
    'Prague': 'Europe/Prague',
    'Pretoria': 'Africa/Johannesburg',
    'Quito': 'America/Lima',
    'Rangoon': 'Asia/Rangoon',
    'Riga': 'Europe/Riga',
    'Riyadh': 'Asia/Riyadh',
    'Rome': 'Europe/Rome',
    'Samara': 'Europe/Samara',
    'Samoa': 'Pacific/Apia',
    'Santiago': 'America/Santiago',
    'Sapporo': 'Asia/Tokyo',
    'Sarajevo': 'Europe/Sarajevo',
    'Saskatchewan': 'America/Regina',
    'Seoul': 'Asia/Seoul',
    'Singapore': 'Asia/Singapore',
    'Skopje': 'Europe/Skopje',
    'Sofia': 'Europe/Sofia',
    'Solomon Is.': 'Pacific/Guadalcanal',
    'Srednekolymsk': 'Asia/Srednekolymsk',
    'Sri Jayawardenepura': 'Asia/Colombo',
    'St. Petersburg': 'Europe/Moscow',
    'Stockholm': 'Europe/Stockholm',
    'Sydney': 'Australia/Sydney',
    'Taipei': 'Asia/Taipei',
    'Tallinn': 'Europe/Tallinn',
    'Tashkent': 'Asia/Tashkent',
    'Tbilisi': 'Asia/Tbilisi',
    'Tehran': 'Asia/Tehran',
    'Tijuana': 'America/Tijuana',
    'Tokelau Is.': 'Pacific/Fakaofo',
    'Tokyo': 'Asia/Tokyo',
    'UTC': 'Etc/UTC',
    'Ulaanbaatar': 'Asia/Ulaanbaatar',
    'Urumqi': 'Asia/Urumqi',
    'Vienna': 'Europe/Vienna',
    'Vilnius': 'Europe/Vilnius',
    'Vladivostok': 'Asia/Vladivostok',
    'Volgograd': 'Europe/Volgograd',
    'Warsaw': 'Europe/Warsaw',
    'Wellington': 'Pacific/Auckland',
    'West Central Africa': 'Africa/Algiers',
    'Yakutsk': 'Asia/Yakutsk',
    'Yerevan': 'Asia/Yerevan',
    'Zagreb': 'Europe/Zagreb'
}


def friendly_to_tz(friendly):
    return TZ_MAPPING.get(friendly, 'Etc/UTC')
