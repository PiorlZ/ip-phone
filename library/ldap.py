import math
from itertools import groupby
from operator import itemgetter
import copy
from library.settings import AD_LOGIN, AD_PASS, AD_SERVER, AD_PORT, LIMIT_PART, LIST_OF_CONTACTS, LIST_OF_ATTR, PHONE_LEN
from ldap3 import Server, Connection, AUTO_BIND_NO_TLS, SUBTREE
from library.Cisco import cisco_xml
from library.Yealink import yealink_xml


def bureau_drop(d):
    """
        Убирает управление из списка для дальнейшей сортировки
    """
    del d['bureau']
    return d


def sort_by_bureau(i):
    """
        Функция для сортировки по управлениям
    """
    return i['bureau']


def sort_by_name(i):
    """
        Функция для сортировки по именам
    """
    return i['name']


def split_long_bureau_list(contact_list_split=None, param=None, limit=None):
    """
        Разбивает длинные списки с управлением на несколько частей для Cisco
    """
    k = 1
    for i in contact_list_split:
        if i['bureau'] == param:
            i['bureau'] = i['bureau'] + ' ч.' + str(math.ceil(k / limit))
            k += 1
    return contact_list_split


def make_contact_list(contact_list_split, phone_len=PHONE_LEN):
    """
        Убирает контакты с None и false, отделяет номера телефонов для записи
    """
    contact_list = []
    for el in contact_list_split:
        if str(el.extensionAttribute10.value).strip() == 'false' or str(
                el.extensionAttribute10.value).strip() == 'None':
            continue
        if len(str(el.telephoneNumber.value)) < phone_len:
            continue
        if str(el.telephoneNumber.value).strip() == 'None' or str(el.telephoneNumber.value).strip() == 'false':           d
            continue
        if str(el.extensionAttribute11.value).strip() == 'false' or str(
                el.extensionAttribute11.value).strip() == 'None':
            department = str(el.extensionAttribute10.value).strip()
        else:
            department = str(el.extensionAttribute11.value).strip()
        str1 = str(el.displayName.value).strip() + ' |' + department
        if str(el.title.value).strip() != 'None' and str(el.title.value).strip() != 'false':
            str1 += ' |' + str(el.title.value).strip()
        phone_number = str(el.telephoneNumber.value).strip()
        if not phone_number.find('\\') == -1:
            phones = phone_number.split('\\')
        else:
            phones = phone_number.split('/')
        phones += ['', '']
        contact_list.append({
            'bureau': str(el.extensionAttribute10.value).strip(),
            'name': str1,
            'phone': phones,
        })
    return contact_list


def short(contact_list):
    """
        Функция для сокращения контактов и уборки непподерживаемых символов (Cisco)
    """
    import re
    for i in contact_list:
        if i['bureau'] == 'Координационно-диспетчерский центр аэропорта':
            i['bureau'] = 'КДЦА'
    for i in contact_list:
        for j in i['person']:
            j['name'] = j['name'].replace('Координационно-диспетчерский центр аэропорта', 'КДЦА')
            j['name'] = j['name'].replace('Служба электросветотехнического обеспечения полетов', 'СЭОП')
            j['name'] = re.sub(r"(#)|(-)|(&)|(%)|(/)|(\")|(\')|(_)|(№)|(\()|(\))|($)", "", j['name'])
    return contact_list


def sort_and_group_contacts_cisco(contact_list, limit_of_records):
    """
        Сортирует и группирует контакты для Cisco
    """
    temp_contact_list = copy.deepcopy(contact_list)
    temp_contact_list.sort(key=sort_by_bureau)
    temp_contact_list = [{'bureau': i, 'person': list(map(bureau_drop, grp))}
                         for i, grp in groupby(temp_contact_list, itemgetter('bureau'))]
    contact_list.sort(key=sort_by_name)
    for i in temp_contact_list:
        if len(i['person']) > limit_of_records:
            contact_list = split_long_bureau_list(contact_list_split=contact_list, param=i['bureau'], limit=limit_of_records)
    contact_list.sort(key=sort_by_bureau)
    contact_list = [{'bureau': i, 'person': list(map(bureau_drop, grp))}
                    for i, grp in groupby(contact_list, itemgetter('bureau'))]
    for i in contact_list:
        i['person'].sort(key=sort_by_name)
    contact_list = short(contact_list)
    return contact_list


def sort_and_group_contacts_yealink(contact_list):
    """
        Сортирует и группирует контакты для Yealink
    """
    contact_list.sort(key=sort_by_bureau)
    contact_list = [{'bureau': i, 'person': list(map(bureau_drop, grp))}
                    for i, grp in groupby(contact_list, itemgetter('bureau'))]
    for i in contact_list:
        i['person'].sort(key=sort_by_name)
    return contact_list


def create_phonebooks_from_ad_base(limit_of_records=LIMIT_PART, list_of_contacts=LIST_OF_CONTACTS, attr=LIST_OF_ATTR, ):
    """
        Главная функция. Создаёт 2 списка. Нужна для подключения базы ад и передачи списка в записыватели.
    """
    with Connection(
            Server(
                AD_SERVER,
                port=AD_PORT
            ),
            auto_bind=AUTO_BIND_NO_TLS,
            user=AD_LOGIN,
            password=AD_PASS
    ) as c:
        cisco_contact_list = []
        yealink_contact_list = []
        for i in list_of_contacts:
            temp_cisco_contact_list = []
            for filial in i['part']:
                c.search(
                    search_base='OU=' + filial['name'] + ',DC=airport,DC=local',
                    search_filter=filial['filter'],
                    search_scope=SUBTREE,
                    attributes=attr,
                    get_operational_attributes=True
                )
                temp_cisco_contact_list += make_contact_list(c.entries)
            temp_yealink_contact_list = copy.deepcopy(temp_cisco_contact_list)
            cisco_contact_list += sort_and_group_contacts_cisco(temp_cisco_contact_list, limit_of_records)
            yealink_contact_list += sort_and_group_contacts_yealink(temp_yealink_contact_list)
        c.unbind()
        cisco_xml(cisco_contact_list)
        yealink_xml(yealink_contact_list)
