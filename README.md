
# ACWC24
**ACWC24** creates distributable files for DLC items, patterns and letters in Animal Crossing City Folk (also known as *Let's Go to the City* in PAL regions). These files can be stored on a server from where it is sent to other people's games. Because the official Nintendo servers have been shut down in 2013, [RiiConnect24](https://rc24.xyz/) was founded, which provides a great service to *reconnect* your Wii to the internet and download DLC. Therefore, this tool was created to make the process of creating distributables less tedious.

# Features
Here's a quick overview of *ACWC24*'s features:
 - Pack distributable items, patterns or both!
 - Easily manage delivered letters
 - Supports all versions and regions!
 - Separate distributables for target regions
 - Create valid U8 archives for distributables
 - Automatically encrypt output files

The game also appears to support DLC NPCs, however, this needs to be investigated.

# Requirements
In order to encrypt WC24 files, the *pyaes* and *rsa* modules are required. You can install them using *pip*:

    pip install pyaes
    pip install rsa
Also, the AES and PEM keys for ACCF are required in order to properly sign the data. I can't share those, unfortunately. You are on your own finding them. If you manage to obtain the keys, put them in *rvforestdl.aes.bin* and *rvforestdl.pem.bin*.
If you don't have those keys, the tool will skip encryption and create the U8 archive only.
In order to add content, put the binary item files (which can be created with *ACDLC*) in the *items* folder. Patterns belong to the *designs* folder.

# Usage
Each distributable has a folder inside the *src* directory. They all require a proper *info.json* file which defines the general parameters for the package:

    {
	    "Regions": [ "E", "P", "J", "K" ],
	    "Unk0": 1,
	    "Unk4": 1,
	    "LetterId": XX,
	    "UnkC": 0,
	    "Unk10": 0,
	    "ItemFile": "<item file name>",
	    "DesignFile": "<pattern file name>",
	    "NpcFile": "<npc file name>",
	    "Paper": "<stationery name>",
	    "Letters": { // optional specified letters for each language
		    "UsEnglish": {
			    "Header": "Dear \n,",
			    "Body": "here is your special item!",
			    "Footer": "from Aurum",
			    "Sender": "Aurum"
		    }
	    }
	}

The target region is used to add the required letter text for each localization (if available). If you don't want to create a package for separate regions, simply change the list to contain the element *All*. The unknown parameters still need to be documented but can be the above values if you just want to distribute items.
Letters for each language are stored in the *Letters* object above. The keys for the different languages are:

| Language | Key | Region |
|--|--|--|
| English (NOA) | UsEnglish | E |
| French (NOA) | UsFrench | E |
| Spanish (NOA) | UsSpanish | E |
| English (NOE) | EuEnglish | P |
| French (NOE) | EuFrench | P |
| Spanish (NOE) | EuSpanish | P |
| German | German | P |
| Italian | Italian | P |
| Japanese | Japanese | J |
| Korean | Korean | K |

It's important to note that a line should never contain more than ~26 characters or the game will not display the letter at all! Make sure to put in line breaks.

You can pack the distributable using the command

    python acwc24.py <dlc name>

If you want to keep the decrypted U8 archive, you can append *--keep_decrypted* or *-k*.