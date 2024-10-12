"""
FLAC to MP3 Converter and File Copier


This Python script traverses a source directory (including its subdirectories),
copies non-FLAC files to a specified output directory, and converts FLAC files to
MP3 format, saving the converted files in a separate output directory (`.jpg` artwork 
files are ignored). The program automatically creates the two output directories if 
they do not already exist, ensuring smooth execution.


Requirements:
- Python 3.x
- Libraries: `pydub`, `mutagen`, `shutil`, `os`
- `ffmpeg` must be installed on your system since `pydub` uses it for audio file conversion.


Author: Aliaksei Maksimenka
Version: 1.0
Date: October 2024
"""
from pydub import AudioSegment
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TCON, TRCK, TDRC, TPE2
import os
import shutil


INPUT_DIRECTORY = 'D:/My documents/Downloads/Music'
OUTPUT_COPY_DIRECTORY = 'D:/My documents/Downloads/OUTPUT'
OUTPUT_CONVERTED_DIRECTORY = 'D:/My documents/Downloads/OUTPUT/CONVERTED'


def convert_flac_to_mp3(flac_file_path, mp3_file_path):
    # Load the FLAC audio
    flac_audio = AudioSegment.from_file(flac_file_path, format="flac")

    # Convert to MP3 with 320 kbps bitrate
    flac_audio.export(mp3_file_path, format="mp3", bitrate="320k")

    # Load FLAC metadata
    flac_file = FLAC(flac_file_path)

    # Open the new MP3 file
    mp3_file = MP3(mp3_file_path, ID3=ID3)

    # print(flac_metadata)
    copy_metadata(flac_file, mp3_file)

    # Save MP3 file with updated metadata
    mp3_file.save()

    print(f"Converted: {flac_file_path} to {mp3_file_path}")


def copy_metadata(flac_file, mp3_file):
    if 'TITLE' in flac_file:
        mp3_file.tags["TIT2"] = TIT2(encoding=3, text=flac_file['TITLE'][0])
    if 'ARTIST' in flac_file:
        mp3_file.tags["TPE1"] = TPE1(encoding=3, text=flac_file['ARTIST'][0])
    if 'ALBUM' in flac_file:
        mp3_file.tags["TALB"] = TALB(encoding=3, text=flac_file['ALBUM'][0])
    if 'GENRE' in flac_file:
        mp3_file.tags["TCON"] = TCON(encoding=3, text=flac_file['GENRE'][0])
    if 'TRACKNUMBER' in flac_file:
        mp3_file.tags["TRCK"] = TRCK(encoding=3, text=flac_file['TRACKNUMBER'][0])
    if 'DATE' in flac_file:
        mp3_file.tags["TDRC"] = TDRC(encoding=3, text=flac_file['DATE'][0])
    if 'ALBUM ARTIST' in flac_file:
        mp3_file.tags["TPE2"] = TPE2(encoding=3, text=flac_file['ALBUM ARTIST'][0])

    # Add artwork if available
    if flac_file.pictures:
        image = flac_file.pictures[0]
        mp3_file.tags.add(
            APIC(
                encoding=3,  # 3 is for utf-8
                mime=image.mime,
                type=3,  # Album front cover
                desc='Cover',
                data=image.data
            )
        )


def copy_converted_files(source_dir, copy_dir, converted_dir):
    # Create output directories if they don't exist
    os.makedirs(copy_dir, exist_ok=True)
    os.makedirs(converted_dir, exist_ok=True)

    file_counter = 0

    # Traverse through all files and subdirectories in the source directory
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            file_path = os.path.join(root, file)

            file_counter += 1
            print(f'file_counter = {file_counter}  file = {file_path}')

            # Check if the file is a .flac file
            if file.lower().endswith('.flac'):
                # Convert FLAC to MP3 and save in the converted_dir
                mp3_file_path = os.path.join(converted_dir, f"{os.path.splitext(file)[0]}.mp3")
                convert_flac_to_mp3(file_path, mp3_file_path)
            elif not file.lower().endswith('.jpg'):  # other files excluding artwork
                # Copy non-FLAC files to the copy_dir (no folder structure)
                shutil.copy(file_path, os.path.join(copy_dir, file))


if __name__ == "__main__":
    copy_converted_files(INPUT_DIRECTORY, OUTPUT_COPY_DIRECTORY, OUTPUT_CONVERTED_DIRECTORY)
