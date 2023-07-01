import os
from library.settings import XML_YEALINK, FOLDER, APACHE, BASE_DIR


def yealink_xml(contact_list, filename=XML_YEALINK, folder=FOLDER, bd=BASE_DIR):  # APACHE
    """
        Записывает контакты в Xml формате для Yealink
    """
    import cx_XML
    if not os.path.exists(os.path.join(bd, folder)):
        os.mkdir(os.path.join(bd, folder))
    output_file = open(filename, "w", encoding='utf-8')
    writer = cx_XML.Writer(output_file, numSpaces=4)
    writer.StartTag("YealinkIPPhoneBook")
    writer.WriteTagWithValue("Title", 'АО "Аэропорт Южно-Сахалинск"')
    for i in contact_list:
        writer.StartTag("Menu", Name=i['bureau'])
        for j in i['person']:
            writer.WriteTagNoValue("Unit",  Name=j['name'], Phone1=j['phone'][0], Phone2=j['phone'][1],
                                   Phone3=j['phone'][2],  default_photo="Resource:")
        writer.EndTag()
    writer.EndTag()
    output_file.close()
