# ACWC24
**ACWC24** creates distributable files for DLC items, patterns and letters in Animal Crossing City Folk (also known as *Let's Go to the City* in PAL regions). These files can be stored on a server from where it is sent to other people's games. Because the official Nintendo servers have been shut down in 2013, [RiiConnect24](https://rc24.xyz/) was founded, which provides a great service to *reconnect* your Wii to the internet and download DLC. Therefore, this tool was created to make the process of creating distributables less tedious.

# Features
Here's a quick overview of *ACWC24*'s features:
 - Pack distributable items, patterns or both!
 - Easily manage delivered letters
 - Supports NTSC-U, PAL, NTSC-J and NTSC-K regions!
 - Separate distributables for target regions
 - Create valid U8 archives for distributables
 - Automatically encrypt output files

The game also appears to support DLC NPCs or something like that, however, this needs to be investigated.

# Requirements
In order to encrypt WC24 files, the *pyaes* and *rsa* modules are required. You can install them using *pip*:

    pip install pyaes
    pip install rsa
Also, the AES and PEM keys for ACCF are required in order to properly sign the data. We can't share those, unfortunately. You are on your own finding them. If you manage to obtain the keys, put them in *rvforestdl.aes.bin* and *rvforestdl.pem.bin*.
If you don't have those keys, the tool will skip encryption and create the U8 archive only.
In order to add content, put the binary item files (which can be created with *ACDLC*) in the *items* folder. Patterns belong to the *designs* folder.

# Usage
Each distributable has a folder inside the *src* directory. They all require a proper *info.json* file which defines the general parameters for the package:

    {
	    "Regions": [ "E", "P", "J", "K" ],
	    "Unk0": 1,
		"Unk4": 1,
		"Unk8": 16,
		"UnkC": 0,
		"Unk10": 0,
		"ItemFile": "<item file name>",
		"DesignFile": "<pattern file name>",
		"NpcFile": "<npc file name>"
	}

The target region is used to add the required letter text for each localization (if available). If you don't want to create a package for separate regions, simply change the list to contain *All*. The unknown parameters still need to be documented.
Letters for each language are stored in separate files:

| Language | File name | Region |
|--|--|--|
| English (NOA) | usEnglish.json | E |
| French (NOA) | usFrench.json | E |
| Spanish (NOA) | usSpanish.json | E |
| English (NOE) | euEnglish.json | P |
| French (NOE) | euFrench.json | P |
| Spanish (NOE) | euSpanish.json | P |
| German | euGerman.json | P |
| Italian | euItalian.json | P |
| Japanese | jpJapanese.json | J |
| Korean | krKorean.json | K |

It's a basic JSON object which looks like this:

    {
		"Paper": "elegant",
		"Sender": "RiiConnect24",
		"Header": "Dear \n,",
		"Body": "Here is a DLC item from\nRiiConnect24. It's an\nRC24 carpet! It'll show\nvisitors that you enjoy\nusing our service!",
		"Footer": "RiiConnect24"
	}

It's important to note that a line should never contain more than 26 characters or the game will not display the letter at all! Make sure to put line breaks.

You can pack the distributable using the command

    python acwc24.py <dlc name>

If you want to keep the decrypted U8 archive, you can append *--keep_decrypted* or *-k*.