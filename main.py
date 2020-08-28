import config
import filecmp
import io
import os.path
import pandas as pd
import pickle
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
    print(bcolors.HEADER + 'Downloading PDF...' + bcolors.ENDC)
    with urllib.request.urlopen(url) as response, open(path, 'wb') as out_file:
        data = response.read()
        out_file.write(data)
    print(bcolors.OKGREEN + 'Complete!' + bcolors.ENDC)
    print()


def compareFiles(file_old, file_new):
    print(bcolors.OKBLUE + 'Comparing old file with new...' + bcolors.ENDC)
    sameFile = filecmp.cmp(file_old, file_new)

    # delete/rename files
    os.remove(file_old)        
    os.rename(file_new, file_old)

    # compare checksums
    if sameFile:
        print(bcolors.FAIL + 'No new copy found.' + bcolors.ENDC)
        print()
        return False
        
    else:
        print(bcolors.OKGREEN + 'New copy found!' + bcolors.ENDC)   
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


def sendEmail(tags):

    def composeEmail():
        print(bcolors.WARNING + 'Sending \'Tags Available\' mail notification...' + bcolors.ENDC)

        # check if multiple tags
        if len(tags) > 1:
            tagSubj = 'Colorado Tags Available!'
            var0 = 'tags are'
            var2 = 'those tags'
            
        else:
            tagSubj = 'Colorado Tag ({0}) Available!'.format(tags[0])
            var0 = 'tag is'
            var2 = 'that tag'

        tagMsg = '''        
The following {0} available:

{1}

https://www.cpwshop.com/purchaseprivilege.page

Get {2}, bitch!

Love,
C
        '''.format(var0, '\n'.join(tags), var2)

        request_url = 'https://api.mailgun.net/v3/{0}/messages'.format(config.sandbox)
        request = requests.post(request_url, auth=('api', config.key), data={
            'from': 'Colorado Tag Check <getthattag@rightnow.com>',
            'to': config.recipients,
            'subject': tagSubj,
            'text': tagMsg
        })
        
        if request.status_code == 200:
            print(bcolors.OKGREEN + 'Message sent for: {0}'.format(tags) + bcolors.ENDC)

        else:
            print(bcolors.FAIL + 'Submission error.' + bcolors.ENDC)
            print(request.json())

    def composeGoneEmail():
        print(bcolors.WARNING + 'Sending \'Tags Gone\' email notification...' + bcolors.ENDC)

        # check if multiple tags
        if len(take_off_list) > 1:
            tagSubj = 'Colorado Tags Gone!'
            var0 = 'tags are'
            var2 = 'them'
            
        else:
            tagSubj = 'Colorado Tag ({0}) is Gone!'.format(take_off_list[0])
            var0 = 'tag is'
            var2 = 'it'

        tagMsg = '''        
The following {0} no longer available:

{1}

Hope you got {2}!

Love,
C
        '''.format(var0, '\n'.join(take_off_list), var2)

        request_url = 'https://api.mailgun.net/v3/{0}/messages'.format(config.sandbox)
        request = requests.post(request_url, auth=('api', config.key), data={
            'from': 'Colorado Tag Check <getthattag@rightnow.com>',
            'to': config.recipients,
            'subject': tagSubj,
            'text': tagMsg
        })
        
        if request.status_code == 200:
            print(bcolors.OKGREEN + 'Message sent for: {0}'.format(take_off_list) + bcolors.ENDC)

        else:
            print(bcolors.FAIL + 'Submission error.' + bcolors.ENDC)
            print(request.json())

    # possible tags
    print('Tags on list: {0}'.format(tags))

    # get tags previously sent
    if os.path.isfile('tags-emailed.pkl'):
        with open('tags-emailed.pkl', 'rb') as f:
            already_emailed = pickle.load(f)
            already_emailed = list(dict.fromkeys(already_emailed)) # remove possible duplicates
            print('Already emailed (tags-emailed.pkl): {0}'.format(already_emailed))
        
        # compare tags_done and tags    
        dont_email = list(set(tags).intersection(already_emailed))   
        print('Don\'t email: {0}'.format(dont_email))
        
        if len(dont_email) > 0:
            # remove 'dont_email' tags out of tags         
            for item in dont_email:
                tags.remove(item)

            # send 'get tags' email
            if len(tags) > 0:
                composeEmail()

            else:
                print('No email needed')        
        
        elif len(tags) > 0:
            composeEmail()

        # update pickle
        emailed_tags = dont_email + tags
        take_off_list = list(set(already_emailed).difference(dont_email))
        print('Removing: {0}'.format(take_off_list))    
        

        if len(take_off_list) > 0:
            composeGoneEmail()

        # save data
        print('Saving tags-emailed.pkl: {0}'.format(emailed_tags))
        with open('tags-emailed.pkl', 'wb') as f:
            pickle.dump(emailed_tags, f)        

    else:
        composeEmail()

        print('Saving tags-emailed.pkl: {0}'.format(tags))

        # save data
        with open('tags-emailed.pkl', 'wb') as f:
            pickle.dump(tags, f)    


def checkTag():
    print('------------------')
    print(bcolors.HEADER + 'Importing tags from file...' + bcolors.ENDC)
    print()

    df = pd.read_csv('code-list.csv',header=None)
    tagArray = []
    pdfText = scanPDF(path)

    for index, field in df.iterrows():
        code = ''.join(e for e in field[0] if e.isalnum())
        print(bcolors.BOLD + 'Checking PDF for ' + code + bcolors.ENDC)

        if code in pdfText:
            print(bcolors.OKGREEN + 'Tag found!' + bcolors.ENDC)
            tagArray.append(code)            
        
        else:
            print(bcolors.FAIL + 'Tag not found.' + bcolors.ENDC)
            
        print()

    print(bcolors.BOLD + 'Import complete.' + bcolors.ENDC)
    print('------------------')
    print()    

    sendEmail(tagArray)

    print()
    print('------------------')
    print()    
    print(bcolors.HEADER + 'FINISHED' + bcolors.ENDC)
    print()


def main():
    print(bcolors.HEADER + 'COLORADO-TAG-CHECK' + bcolors.ENDC)
    print('Checking for existing file...')
    pathExists  = os.path.isfile(path)
    path2Exists = os.path.isfile(path2)

    if pathExists:
        print('Found.')
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
            print(bcolors.HEADER + 'FINISHED' + bcolors.ENDC)
            print()

    else:
        print('Not found.')
        print()
        downloadFile(url, path)
        checkTag()


if __name__ == '__main__':
    main()
