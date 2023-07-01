from library.settings import XML_CISCO, FOLDER, BASE_DIR, DIRECTORY, CHILD_DIR
import cx_XML
import os


def get_dir(counter, person, cd=CHILD_DIR, folder=FOLDER, bd=BASE_DIR):
    """
        Создаёт файлы для Cisco в нужной директории
    """
    if not os.path.exists(os.path.join(bd, folder, cd)):
        os.mkdir(os.path.join(bd, folder, cd))
    filename = str(counter) + '.xml'
    output_file = open(os.path.join(bd, folder, cd, filename), "w", encoding='utf-8')
    writer = cx_XML.Writer(output_file, numSpaces=4)
    writer.StartTag("CiscoIPPhoneDirectory")
    writer.WriteTagWithValue("Title", person['bureau'])
    writer.WriteTagWithValue("Prompt", 'Директория')
    for j in person['person']:
        writer.StartTag("DirectoryEntry")
        writer.WriteTagWithValue("Name", j['name'])
        writer.WriteTagWithValue("Telephone", j['phone'][0])
        writer.EndTag()
    writer.EndTag()
    output_file.close()


def cisco_xml(contact_list, filename=XML_CISCO, folder=FOLDER, bd=BASE_DIR, path_to_cisco_bureau=DIRECTORY,):
    """
        Записывает контакты в Xml формате для Cisco
    """
    if not os.path.exists(os.path.join(bd, folder)):
        os.mkdir(os.path.join(bd, folder))
    output_file = open(filename, "w", encoding='utf-8')
    writer = cx_XML.Writer(output_file, numSpaces=4)
    writer.StartTag("CiscoIPPhoneMenu")
    writer.WriteTagWithValue("Title", 'АО "Аэропорт Южно-Сахалинск"')
    writer.WriteTagWithValue("Prompt", 'Меню')
    counter = 1
    for i in contact_list:
        writer.StartTag("MenuItem")
        writer.WriteTagWithValue("Name", i['bureau'])
        writer.WriteTagWithValue("URL", path_to_cisco_bureau + str(counter))
        get_dir(counter, i)
        counter += 1
        writer.EndTag()
    writer.EndTag()
    output_file.close()
