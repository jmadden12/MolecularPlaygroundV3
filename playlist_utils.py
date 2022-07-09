from distutils.log import error
import os
import zipfile

ASSET_FILE_EXT = ".pdb"

SCRIPT_FILE_EXT = ".spt"

PLAYLIST_FILE_EXT = ".playlist"

PLAYLIST_DIRECTORY = "playlists/"

TEMPFILE_DIRECTORY = "temp/"

ZIPFILE_DIRECTORY = "zips/"


def construct_script_string(playlist_name):
    path = PLAYLIST_DIRECTORY + playlist_name + "/"
    playlist_directory_file_list = []

    with os.scandir(path) as it:
        for entry in it:
            playlist_directory_file_list.append(entry.name)

    ## Check if playlist file exists in playlist directory
    playlist_filename = playlist_name + PLAYLIST_FILE_EXT
    if(playlist_filename not in playlist_directory_file_list):
        print("Playlist file " + playlist_filename +  "not found.")
        return -1
    
    playlist_file = open(path + playlist_filename, 'r')
    script_string = ""

    for line in playlist_file:
        line = line.rstrip()
        error_string = ""
        script_filename = line + SCRIPT_FILE_EXT
        asset_filename = line + ASSET_FILE_EXT
        if(script_filename not in playlist_directory_file_list):
            error_string += "File " + script_filename + " not found in playlist directory. "
        if(asset_filename not in playlist_directory_file_list):
            error_string += "File " + asset_filename + " not found in playlist directory. "
        if(len(error_string) != 0):
            print(error_string)
            return -1
        
        script_string += "load " + path + asset_filename + "\n"
        script_string += "script " + path + script_filename + "\n"
    return script_string

def create_playlist_script_file(playlist_name):
    tempfile = open(TEMPFILE_DIRECTORY + playlist_name + SCRIPT_FILE_EXT, 'w')
    script_string = construct_script_string(playlist_name)
    if(playlist_name == -1):
        tempfile.close()
        return -1
    tempfile.write(script_string)

def cleanup_script_files():
    with os.scandir(TEMPFILE_DIRECTORY) as it:
        for entry in it:
            os.remove(TEMPFILE_DIRECTORY + entry.name)


### ZIPFILE ###

def is_pl_zip_valid(name):
    zip = zipfile.ZipFile(ZIPFILE_DIRECTORY + name + ".zip")
    file_list = zip.infolist()
    file_name_list = []
    for zipinfo_obj in file_list:
        file_name_list.append(zipinfo_obj.filename)
    playlist_filename = name + PLAYLIST_FILE_EXT
    access_filename = name + "/" + playlist_filename
    if(access_filename in file_name_list == False):
        print(access_filename)
        print(file_name_list)
        return False
    playlist_file = zip.open(access_filename)
    while((line := playlist_file.readline().decode()) != ""):
        line = line.rstrip()
        error_string = ""
        script_filename = name + "/" + line + SCRIPT_FILE_EXT
        asset_filename = name + "/" + line + ASSET_FILE_EXT
        if(script_filename not in file_name_list):
            error_string += "File " + script_filename + " not found in playlist zip. "
        if(asset_filename not in file_name_list):
            error_string += "File " + asset_filename + " not found in playlist zip. "
        if(len(error_string) != 0):
            print(error_string)
            return False
    return True

def import_playlist_zip(name):
    zip = zipfile.ZipFile(ZIPFILE_DIRECTORY + name + ".zip")

    zip.extractall(path=PLAYLIST_DIRECTORY)

    os.remove(ZIPFILE_DIRECTORY + name + ".zip")



    
    


        
    
    



