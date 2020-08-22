import config
import hashlib
import io
import os.path
import pandas as pd
import requests
import urllib.request
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import PDFPageAggregator
from pdfminer3.converter import TextConverter


## vars
url   = 'https://cpw.state.co.us/Documents/Leftover.pdf'
path  = 'Leftover.pdf'
path2 = 'Leftover_new.pdf'


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'    
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'


## functions
def downloadFile(url, path):
    print(bcolors.HEADER + "Downloading PDF..." + bcolors.ENDC)
    with urllib.request.urlopen(url) as response, open(path, 'wb') as out_file:
        data = response.read()
        out_file.write(data)
    print(bcolors.OKGREEN + "Complete!" + bcolors.ENDC)
    print()


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def compareFiles(file_old, file_new):
    print(bcolors.OKBLUE + "Comparing old file with new..." + bcolors.ENDC)

    # get checksums
    check1 = md5(file_old)
    check2 = md5(file_new)

    # delete/rename files
    os.remove(file_old)        
    os.rename(file_new, file_old)

    # compare checksums
    if check1 == check2:
        print(bcolors.FAIL + "No new copy found." + bcolors.ENDC)
        print()
        return False
        
    else:
        print(bcolors.OKGREEN + "New copy found!" + bcolors.ENDC)   
        print()  
        return True


def scanPDF(path):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    with open(path, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            page_interpreter.process_page(page)
        pdfText = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()

    return pdfText


def sendEmail():
    print(bcolors.WARNING + "Sending email notification..." + bcolors.ENDC)

    request_url = 'https://api.mailgun.net/v3/{0}/messages'.format(config.sandbox)
    request = requests.post(request_url, auth=('api', config.key), data={
        'from': 'Colorado Tag Check <getthattag@rightnow.com>',
        'to': config.recipient,
        'subject': 'Colorado Tag (#####) Available!',
        'text': 'Get that tag, bitch!'
    })
    
    if request.status_code == 200:
        print(bcolors.OKGREEN + "Message sent!" + bcolors.ENDC)
        print()

    else:
        print(bcolors.FAIL + "Submission error." + bcolors.ENDC)
        print(request.json())
        print()


def checkTag():
    print('------------------')
    print(bcolors.HEADER + "Importing tags from file..." + bcolors.ENDC)
    print()

    df = pd.read_csv('code-list.csv',header=None)
    for index, field in df.iterrows():
        code = ''.join(e for e in field[0] if e.isalnum())
        print(bcolors.BOLD + "Checking PDF for " + code + bcolors.ENDC)     

        pdfText = scanPDF(path)

        if code in pdfText:
            print(bcolors.OKGREEN + "Tag found!" + bcolors.ENDC)   
            sendEmail()
        
        else:
            print(bcolors.FAIL + "Tag not found." + bcolors.ENDC)
            print()

    print(bcolors.BOLD + "Import complete." + bcolors.ENDC)
    print()
    print('------------------')
    print(bcolors.HEADER + "FINISHED" + bcolors.ENDC)


def main():
    print(bcolors.HEADER + "COLORADO-TAG-CHECK" + bcolors.ENDC)
    print("Checking for existing file...")
    pathExists  = os.path.isfile(path)
    path2Exists = os.path.isfile(path2)

    if pathExists:
        print("Found.")
        print()

        # delete copy just in case
        if path2Exists:
            os.remove(path2)

        # download new copy and compare
        downloadFile(url, path2)        
        newUpdate = compareFiles(path, path2) # returns True if files are same

        if newUpdate:
            checkTag()
        else:
            print(bcolors.HEADER + "FINISHED" + bcolors.ENDC)         

    else:
        print("Not found.")
        print()
        downloadFile(url, path)
        checkTag()


if __name__ == '__main__':
    main()
