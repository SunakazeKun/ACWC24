import argparse
import json
import os

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


def create_letter(letterpath: str):
    with open(letterpath, "r", encoding="utf8") as f:
        data = json.load(f)

    default_attributes = bytes.fromhex("00000000000000000000000000000001")
    message_attributes = bytes.fromhex("00000002140000000000000000000000")
    text_mappings = [
        ("", default_attributes),
        (data["Header"], message_attributes),
        (data["Body"], default_attributes),
        (data["Footer"], default_attributes),
        (data["Sender"], default_attributes),
        ("{0}".format(PAPERS.index(data["Paper"]) + 400), default_attributes),
        ("", default_attributes)
    ]

    bmg = Bmg()

    for mapping in text_mappings:
        message = Message()
        message.text = mapping[0]
        message.unk4 = mapping[1]
        bmg.get_messages().append(message)

    return bmg.save()


def create(dlcname: str, keep_decrypted: bool = False):
    srcpath = "src/" + dlcname

    if not os.path.isdir(srcpath):
        print("Can't find " + dlcname)
        return

    dlcinfo = json.load(open(srcpath + "/info.json", "r"))
    infobin = bytearray(20)
    put_uint32(infobin, 0x00, dlcinfo["Unk0"])
    put_uint32(infobin, 0x04, dlcinfo["Unk4"])
    put_uint32(infobin, 0x08, dlcinfo["Unk8"])
    put_uint32(infobin, 0x0C, dlcinfo["UnkC"])
    put_uint32(infobin, 0x10, dlcinfo["Unk10"])

    for region in dlcinfo["Regions"]:
        archive = U8()
        archive.add_file("info.bin", infobin)

        itemfile = dlcinfo["ItemFile"]
        designfile = dlcinfo["DesignFile"]
        npcfile = dlcinfo["NpcFile"]

        if itemfile:
            archive.add_file("item.bin", read_file("items/" + itemfile))

            if region == "E" or region == "All":
                archive.add_file("ltrue.bmg", create_letter(srcpath + "/usEnglish.json"))
                archive.add_file("ltruf.bmg", create_letter(srcpath + "/usFrench.json"))
                archive.add_file("ltrus.bmg", create_letter(srcpath + "/usSpanish.json"))
            elif region == "P" or region == "All":
                archive.add_file("ltree.bmg", create_letter(srcpath + "/euEnglish.json"))
                archive.add_file("ltref.bmg", create_letter(srcpath + "/euFrench.json"))
                archive.add_file("ltreg.bmg", create_letter(srcpath + "/euGerman.json"))
                archive.add_file("ltrei.bmg", create_letter(srcpath + "/euItalian.json"))
                archive.add_file("ltres.bmg", create_letter(srcpath + "/euSpanish.json"))
            elif region == "J" or region == "All":
                archive.add_file("ltrjj.bmg", create_letter(srcpath + "/jpJapanese.json"))
            elif region == "K" or region == "All":
                archive.add_file("ltrkk.bmg", create_letter(srcpath + "/krKorean.json"))
        if designfile:
            archive.add_file("design.bin", read_file("designs/" + designfile))
        if npcfile:
            print("NPCs are not supported yet.")

        outbin = archive.save()
        outpath = "build/" + dlcname + region + ".arc"

        if is_wc24_keys_available():
            if keep_decrypted:
                write_file(outpath, outbin)
            outpath += ".wc24"
            outbin = encrypt(outbin)
        else:
            print("Skipped RSA-AES signing due to missing key file.")

        write_file(outpath, outbin)


def extract(dlcname: str):
    # Todo: Actually create this, duh...
    pass


parser = argparse.ArgumentParser(description="ACWC24 -- ACCF distributable creation tool by Aurum")
parser.add_argument("name", type=str)
parser.add_argument("-k", "--keep_decrypted", action="store_true")
args = parser.parse_args()

if args.name:
    create(args.name, args.keep_decrypted)
