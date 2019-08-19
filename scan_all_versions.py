import DaVinciResolveScript as dvr
import os
import re
import string

def get_all_folders(root_folder):

    sub_folders = []

    if len(root_folder.GetSubFolders()) <1:
        sub_folders += [root_folder]
        return sub_folders

    else:
        for k,v in root_folder.GetSubFolders().iteritems():
            sub_folders += get_all_folders(v)

    return sub_folders + [root_folder]


def find_clip_bin(root_folder):

    sub_folders = root_folder.GetSubFolders()

    for k,v in sub_folders.iteritems():
        if v.GetName() == 'Bin 1':
            inserted_clips = v.GetClips()

    all_folders = get_all_folders(root_folder)

    for folder in all_folders:
        folder_clips = folder.GetClips()

        for i, clip in folder_clips.iteritems():
            if current_clip.GetName() == clip.GetName():
                return folder


def find_versions_from_path(clip_path):
    file_name = os.path.basename(clip_path)
    directory = os.path.dirname(clip_path)

    re_pattern = '(.*)([_,.]v[\d]{2,4})(.[^.]*)$'
    pattern = re.compile('(.*)([_,.]v[\d]{2,4})(.[^.]*)$')
    result = pattern.match(file_name)

    old_version = int(filter(lambda x: x.isdigit(), result.group(2)))

    found_versions = []
    for i in os.listdir(directory):
        result = pattern.match(i)
        if result:
            found_versions.append(
                {
                'file_name': i,
                'version': int(filter(lambda x: x.isdigit(), result.group(2))),
                'directory': directory,
                'filepath': os.path.join(directory, i),
                'old_version': old_version
                }
                )
    return found_versions

def add_new_versions(found_versions, ms):
    new_clips = []
    for version in found_versions:
        if version['version'] > version['old_version']:
            new_clips.append(ms.AddItemsToMediaPool(version['filepath']))
        
    print "Added:"
    for clip in new_clips:
        for k,v in clip.iteritems():
            print '%s -> %s' % (v.GetName(), v.GetClipProperty('File Path'))

def add_old_versions(found_versions, ms):
    new_clips = []
    for version in found_versions:
        if version['version'] < version['old_version']:
            new_clips.append(ms.AddItemsToMediaPool(version['filepath']))

    print "Added:"
    for clip in new_clips:
        for k,v in clip.iteritems():
            print '%s -> %s' % (v.GetName(), v.GetClipProperty('File Path'))

def add_all_versions(found_versions, ms):
    new_clips = []
    for version in found_versions:
        new_clips.append(ms.AddItemsToMediaPool(version['filepath']))

    print "Added:"
    for clip in new_clips:
        for k,v in clip.iteritems():
            print '%s -> %s' % (v.GetName(), v.GetClipProperty('File Path'))


resolve = dvr.scriptapp('Resolve')
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
ms = resolve.GetMediaStorage()   
tl = proj.GetCurrentTimeline()
mp = proj.GetMediaPool()
root_folder = mp.GetRootFolder()


#Get the current clip
current_clip = tl.GetCurrentVideoItem()


#get the item in the media pool
mp_item = current_clip.GetMediaPoolItem()

if not mp_item :
    print 'Error Clips is missing. Move the timeline to an available clip.'
else:

    #get the filepath
    mp_properties = mp_item.GetClipProperty()
    clip_path = mp_properties['File Path']

    #look for other versions
    found_versions = find_versions_from_path(clip_path)

    # set bin to clip's
    clips_bin = find_clip_bin(root_folder)
    mp.SetCurrentFolder(clips_bin)

    #add new clips
    add_all_versions(found_versions, ms)
