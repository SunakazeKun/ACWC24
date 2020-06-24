import argparse
import json

from tools.bitconv import put_uint32
from tools.bmg import Bmg, Message
from tools.files import read_file, write_file
from tools.u8 import U8
from tools.wc24 import is_wc24_keys_available, decrypt, encrypt

PAPERS = ["butterfly", "airmail", "New_Year_s_cards", "lacy", "cloudy", "petal", "snowy", "maple_leaf", "lined",
          "notebook", "flowery", "polka_dot", "weathered", "ribbon", "sparkly", "vine", "formal", "snowman", "card",
          "leopard", "cow", "camouflage", "hamburger", "piano", "Nook", "invite_card", "birthday_card", "four_leaf",
          "town_hall", "Tortimer", "insurance", "academy", "lovely", "rainbow", "Egyptian", "lotus", "tile", "mosaic",
          "elegant", "town_view", "Chinese", "ocean", "industrial", "fireworks", "floral", "mushroom", "star",
          "composer", "bathtub", "SMB3", "cool", "forest", "bubble", "buttercup", "tartan", "plaid", "lemon_lime",
          "crater", "bejeweled", "geometric", "southwest", "night_sky", "chic", "goldfish", "Halloween", "lantern",
          "auction", "bulletin"]

DEFAULT_HEADERS = {
    "UsEnglish": "Dear \n,",
    "UsFrench": "À \n,",
    "UsSpanish": "¡Hola, \n!",
    "EuEnglish": "Dear \n,",
    "EuFrench": "À \n,",
    "EuSpanish": "¡Hola, \n!",
    "German": "Hallo \n,",
    "Italian": "Ciao \n,",
    "Japanese": "Dear \n,",  # placeholder
    "Korean": "Dear \n,"  # placeholder
}
DEFAULT_BODIES = {
    "UsEnglish": "Thank you for using\nRiiConnect24. Attached is\na present from us:\n{0}\nEnjoy!",
    "UsFrench": "Merci d'utiliser\nRiiConnect24. Un cadeau\nde notre part est attaché\nà cette lettre:\n{0}\nProfitez-en bien!",
    "UsSpanish": "Gracias por usar\nRiiConnect24. Te enviamos\nun regalo de nuestra parte:\n{0}\n¡Que lo disfrutes!",
    "EuEnglish": "Thank you for using\nRiiConnect24. Attached is\na present from us:\n{0}\nEnjoy!",
    "EuFrench": "Merci d'utiliser\nRiiConnect24. Un cadeau\nde notre part est attaché\nà cette lettre:\n{0}\nProfitez-en bien!",
    "EuSpanish": "Gracias por usar\nRiiConnect24. Te enviamos\nun regalo de nuestra parte:\n{0}\n¡Que lo disfrutes!",
    "German": "Vielen Dank, dass du\nRiiConnect24 nutzt. Anbei\nfindest du ein Geschenk\nvon uns:\n{0}\nViel Spaß!",
    "Italian": "Grazie per aver usato\nRiiConnect24. Abbiamo\nallegato un regalo da\nparte nostra:\n{0}\nDivertitevi!",
    "Japanese": "Thank you for using\nRiiConnect24. Attached is\na present from us:\n{0}\nEnjoy!",  # placeholder
    "Korean": "Thank you for using\nRiiConnect24. Attached is\na present from us:\n{0}\nEnjoy!"  # placeholder
}


def get_item_name(itemdata, off):
    return itemdata[off:off+0x22].decode("utf-16-be").strip("\0")


def get_item_names(itemdata):
    ret = dict()
    ret["Japanese"] = get_item_name(itemdata, 0x012)
    ret["UsEnglish"] = get_item_name(itemdata, 0x034)
    ret["UsSpanish"] = get_item_name(itemdata, 0x056)
    ret["UsFrench"] = get_item_name(itemdata, 0x078)
    ret["EuEnglish"] = get_item_name(itemdata, 0x09A)
    ret["German"] = get_item_name(itemdata, 0x0BC)
    ret["Italian"] = get_item_name(itemdata, 0x0DE)
    ret["EuSpanish"] = get_item_name(itemdata, 0x100)
    ret["EuFrench"] = get_item_name(itemdata, 0x122)
    ret["Korean"] = get_item_name(itemdata, 0x144)
    return ret


def create_letter(dlc_info: str, locale: str, item_names: dict):
    paper = dlc_info["Paper"] if "Paper" in dlc_info else PAPERS[0]
    # Check if letter exists for specified locale
    if "Letters" in dlc_info and locale in dlc_info["Letters"]:
        data = dlc_info["Letters"][locale]
    # Create a dummy letter from RiiConnect24 if the data cannot be found
    else:
        data = dict()
        data["Header"] = DEFAULT_HEADERS[locale]
        data["Body"] = DEFAULT_BODIES[locale].format(item_names[locale])
        data["Footer"] = "RiiConnect24"
        data["Sender"] = "RiiConnect24"
        data["Paper"] = paper

    # Map text attributes to text
    default_attributes = bytes.fromhex("00000000000000000000000000000001")
    header_attributes = bytes.fromhex("00000002140000000000000000000000")
    text_mappings = [
        ("", default_attributes),
        (data["Header"], header_attributes),
        (data["Body"], default_attributes),
        (data["Footer"], default_attributes),
        (data["Sender"], default_attributes),
        ("{0}".format(PAPERS.index(paper) + 400), default_attributes),
        ("", default_attributes)
    ]

    # Create and store the actual BMG data
    bmg = Bmg()

    for mapping in text_mappings:
        message = Message()
        message.text = mapping[0]
        message.unk4 = mapping[1]
        bmg.get_messages().append(message)

    return bmg.save()


def create(dlc_name: str, keep_decrypted: bool = False):
    dlc_info = json.loads(read_file("src/" + dlc_name + ".json"))

    # Create info.bin
    info_bin = bytearray(20)
    put_uint32(info_bin, 0x00, dlc_info["Unk0"])
    put_uint32(info_bin, 0x04, dlc_info["Unk4"])
    put_uint32(info_bin, 0x08, dlc_info["LetterId"])
    put_uint32(info_bin, 0x0C, dlc_info["UnkC"])
    put_uint32(info_bin, 0x10, dlc_info["Unk10"])

    item_file_name = dlc_info["ItemFile"]
    design_file_name = dlc_info["DesignFile"]
    npc_file_name = dlc_info["NpcFile"]

    if item_file_name:
        item_data = read_file("items/" + item_file_name)
        itemnames = get_item_names(item_data)
    else:
        item_data = None
        itemnames = None
    design_data = read_file("designs/" + design_file_name) if design_file_name else None
    npc_data = read_file("npcs/" + npc_file_name) if npc_file_name else None

    # Create separate distributables for each target region
    for region in dlc_info["Regions"]:
        # Create basic archive
        archive = U8()
        archive.add_file("info.bin", info_bin)

        # Add contents to archive
        if item_data:
            archive.add_file("item.bin", item_data)

            if region == "E" or region == "All":
                archive.add_file("ltrue.bmg", create_letter(dlc_info, "UsEnglish", itemnames))
                archive.add_file("ltruf.bmg", create_letter(dlc_info, "UsFrench", itemnames))
                archive.add_file("ltrus.bmg", create_letter(dlc_info, "UsSpanish", itemnames))
            if region == "P" or region == "All":
                archive.add_file("ltree.bmg", create_letter(dlc_info, "EuEnglish", itemnames))
                archive.add_file("ltref.bmg", create_letter(dlc_info, "EuFrench", itemnames))
                archive.add_file("ltreg.bmg", create_letter(dlc_info, "German", itemnames))
                archive.add_file("ltrei.bmg", create_letter(dlc_info, "Italian", itemnames))
                archive.add_file("ltres.bmg", create_letter(dlc_info, "EuSpanish", itemnames))
            if region == "J" or region == "All":
                archive.add_file("ltrjj.bmg", create_letter(dlc_info, "Japanese", itemnames))
            if region == "K" or region == "All":
                archive.add_file("ltrkk.bmg", create_letter(dlc_info, "Korean", itemnames))
        if design_data:
            archive.add_file("design.bin", design_data)
        if npc_data:
            archive.add_file(npc_file_name, npc_data)

        # Save and encrypt the archive if possible
        output = archive.save()
        out_path = "build/" + dlc_name + "_" + region + ".arc"

        if is_wc24_keys_available():
            if keep_decrypted:
                write_file(out_path, output)
            out_path += ".wc24"
            output = encrypt(output)
        else:
            print("Skipped RSA-AES signing due to missing key(s).")

        write_file(out_path, output)


def extract(dlcname: str):
    # Todo: Actually create this, duh...
    pass


parser = argparse.ArgumentParser(description="ACWC24 -- ACCF distributable creation tool by Aurum")
parser.add_argument("name", type=str)
parser.add_argument("-k", "--keep_decrypted", action="store_true")
args = parser.parse_args()

if args.name:
    create(args.name, args.keep_decrypted)
