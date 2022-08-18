from distutils.log import error
import os
from pydoc import resolve
import zipfile


RELATIVE_PATH = "/Users/localadmin/MolecularPlayground2022/MolecularPlaygroundV3/"

ASSET_FILE_EXT = [".pdb"]

SCRIPT_FILE_EXT = ".spt"

PLAYLIST_FILE_EXT = ".txt"

PLAYLIST_DIRECTORY = RELATIVE_PATH + "playlists/"

TEMPFILE_DIRECTORY = RELATIVE_PATH + "temp/"

ZIPFILE_DIRECTORY = RELATIVE_PATH + "zips/"

ASSET_DIRECTORY = RELATIVE_PATH + "assets/"

DEFAULT_DIRECTORY = ASSET_DIRECTORY + "defaults/"

def resolve_asset_file_ext(asset_name):
    entry_list = os.listdir(ASSET_DIRECTORY)
    for extension in ASSET_FILE_EXT:
        if(asset_name + extension in entry_list):
            return asset_name + extension
    return -1

def grab_playlist_scripts_models(playlist_name):
    grab_result = []
    dir_entry_list = os.listdir(ASSET_DIRECTORY)
    if((entry_list := playlist_file_to_list(playlist_name)) == -1):
        return -1
    for item in entry_list:
        playlist_entry = [] 
        if((full_asset_name := resolve_asset_file_ext(item)) == -1):
            continue
        playlist_entry.append(full_asset_name)
        if(item + SCRIPT_FILE_EXT in dir_entry_list):
            playlist_entry.append(item + SCRIPT_FILE_EXT)
        else:
            playlist_entry.append("defaults/default_script.spt")
        grab_result.append(playlist_entry)
    if(len(grab_result) == 0):
        print("Playlist " + playlist_name + " has no corresponding assets in database.")
        return -1
    return grab_result


def generate_playlist_script_string(playlist_name):
    script_string = ""
    if((grab_result := grab_playlist_scripts_models(playlist_name)) == -1):
        return -1
    for entry in grab_result:
        script_string += "load " + ASSET_DIRECTORY + entry[0] + "\n"
        script_string += "script " + ASSET_DIRECTORY + entry[1] + "\n"
    return script_string

    

def playlist_file_to_list(playlist_name):
    pl_filename = PLAYLIST_DIRECTORY + playlist_name + PLAYLIST_FILE_EXT
    if(os.path.exists(pl_filename) == False):
        return -1
    fd = open(pl_filename)
    entry_list = []
    while((line := fd.readline().rstrip()) != ""):
        entry_list.append(line)
    return entry_list



def create_playlist_script_file(playlist_name):
    tempfile = open(TEMPFILE_DIRECTORY + playlist_name + SCRIPT_FILE_EXT, 'w')
    script_string = generate_playlist_script_string(playlist_name)
    if(playlist_name == -1):
        tempfile.close()
        return -1
    tempfile.write(script_string)

def create_playlist_json_file(playlist_name):
    tempfile = open(TEMPFILE_DIRECTORY + playlist_name + ".json", 'w')
    if(playlist_name == -1):
        tempfile.close()
        return -1
    json_string = "{\"startup_script\" : \"" + TEMPFILE_DIRECTORY + playlist_name + SCRIPT_FILE_EXT + "\" , \"banner_text\" : \"" + playlist_name + "\"}\n"
    print(json_string)
    tempfile.write(json_string)

def list_of_playlists():
    list_of_files = os.listdir(PLAYLIST_DIRECTORY)
    to_return = []
    for item in list_of_files:
        if(os.path.splitext(item)[1] == PLAYLIST_FILE_EXT):
            to_return.append(os.path.splitext(item)[0])
    return to_return

    

def cleanup_script_files():
    with os.scandir(TEMPFILE_DIRECTORY) as it:
        for entry in it:
            os.remove(TEMPFILE_DIRECTORY + entry.name)

#### DEPRECATED PLAYLIST SYSTEM #####

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
    script_string += "loop on\n"
    return script_string

### ZIP ###
    
    
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

def listof_valid_playlists():
    valid_playlists = []
    with os.scandir(PLAYLIST_DIRECTORY) as it:
        for entry in it:
            if(entry.is_dir()):
                if(construct_script_string(entry.name) != -1):
                    valid_playlists.append(entry.name)
    return valid_playlists

        
    
    



