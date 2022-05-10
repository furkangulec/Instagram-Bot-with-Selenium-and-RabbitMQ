#UserDetectFromHashtagComments

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import pandas as pd
import time
from time import sleep
import re

import pika
import sys

import chromedriver_autoinstaller


class UserDetectFromHashtag:

    def start(username, password):

        chromedriver_autoinstaller.install() 
        driver = webdriver.Chrome()


        #region Login to Instagram
        driver.get("https://instagram.com")
        sleep(5)

        login_username = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"input[name='username']")))
        login_password = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"input[name='password']")))

        login_username.clear()
        login_password.clear()
        login_username.send_keys(username)
        login_password.send_keys(password)

        log_in = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"button[type='submit']"))).click()

        sleep(5)
        #region If there is a two-factor authentication
        protection = input("When you are ready, just click enter button!")


        try:
            not_now = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//button[contains(text(),'Şimdi Değil')]"))).click()
            not_now2 = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//button[contains(text(),'Şimdi Değil')]"))).click()
        except Exception as ex:
            print("Not Now Button Error")

        #endregion If there is a two-factor authentication

        #endregion Login to Instagram


        #We will detect posts from these hashtags
        hashtag_list = ["nft", "nfts", "nftartist", "nftcommunity", "nftartgallery", "nftart", "nftcollectors", 
        "nftcolletibles", "openseanft", "nftinvestor",  "nftgram", "polygonnft"]

    
        #region RabbitMQ Connection
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

        channel = connection.channel()
       
        channel.queue_declare(queue='hashtag-queue', durable=True) #We created a queue named durable-queue #users-from-hashtag-queue
        #endregion RabbitMQ Connection

        

        #region User detection from hashtag comments

        while 1:
            for hashtag in hashtag_list:
                print("HASHTAG: ", hashtag)

                #region We are going to hashtag
                page = driver.get("https://www.instagram.com/explore/tags/" + hashtag)
          
                #endregion We are going to hashtag

                #region Window scrolling for 5 times
                for i in range(0, 5):
                    driver.execute_script("window.scrollBy(0,1000000)")
                    time.sleep(5)
                #endregion Window scrolling for 5 times

                #region We are going to collect post links
                all_links = driver.find_elements_by_tag_name('a')
                all_links = [link.get_attribute('href') for link in all_links]
                #endregion We are going to collect post links

                #region We are going to edit links that we collected because there are some unrelated links
                post_links = []
                for old_url in all_links:
                    try:
                        new_url = re.findall("https://www.instagram.com/p/.*", old_url)[0]
                    except Exception as ex:
                        print("Editing Post URL Error: ", ex)
                        new_url = ""

                    if new_url:
                        post_links.append(new_url)
                #endregion We are going to edit links that we collected because there are some unrelated links

                #region We are going to collect comments and usernames from post that we collected and send to the queue
                user_names = []
                user_comments = []

                for post_link in post_links:
                    post = driver.get(post_link)
                    sleep(5)


                    #TODO Load more comments
                    # try:
                    #     load_more_comment = driver.find_element_by_css_selector('.MGdpg > button:nth-child(1)')
                    #     print("Found {}".format(str(load_more_comment)))
                    #     i = 0
                    #     while load_more_comment.is_displayed() and i < int(sys.argv[2]):
                    #         load_more_comment.click()
                    #         time.sleep(1.5)
                    #         load_more_comment = driver.find_element_by_css_selector('.MGdpg > button:nth-child(1)')
                    #         print("Found {}".format(str(load_more_comment)))
                    #         i += 1
                    # except Exception as e:
                    #     print(e)
                    #     pass

                    
                    container = driver.find_elements_by_class_name('C4VMK ')

                    for c in container:
                        comment = c.find_element_by_class_name('MOdxS')
                        content = comment.find_element_by_tag_name('span').text
                        content = content.replace('\n', ' ').strip().rstrip()

                        username = c.find_element_by_class_name('sqdOP').text

                        channel.basic_publish(exchange='', routing_key='hashtag-queue', body=username, properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE))
                        print(f"'{username}' is sent to queue")

                        user_names.append(username) #TODO You can delete it is unnecessary
                        user_comments.append(content) #TODO You can delete it is unnecessary

                #endregion We are going to collect comments and usernames from post that we collected and send to the queue

        connection.close()

        #endregion User detection from hashtag comments