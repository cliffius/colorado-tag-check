import urllib.request
import os.path
import hashlib

## vars
url   = 'https://cpw.state.co.us/Documents/Leftover.pdf'
path  = 'downloads/Leftover.png'
path2 = 'downloads/Leftover_new.png'


## functions
def downloadFile(url, path):
    with urllib.request.urlopen(url) as response, open(path, 'wb') as out_file:
        data = response.read()
        out_file.write(data)


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def compareFiles(file_old, file_new):
    # get checksums
    check1 = md5(file_old)
    check2 = md5(file_new)

    # delete/rename files
    os.remove(file_old)        
    os.rename(file_new, file_old)

    # compare checksums
    if check1 == check2:        
        return True
    else:
        return False


def checkTag():
    print('Check the tag')
    #Check for code -> request code (import via csv?)
    #If exists, email
    #If not, wait and return to main


def main():
    pathExists  = os.path.isfile(path)

    if pathExists:
        downloadFile(url, path2)        
        noUpdate = compareFiles(path, path2) # returns True if files are same
        if noUpdate:
            print('No update')
        else:
            checkTag()
    else:
        downloadFile(url, path)
        checkTag()


if __name__ == '__main__':
    main()
