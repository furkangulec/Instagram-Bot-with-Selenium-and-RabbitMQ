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

from selenium import webdriver
import chromedriver_autoinstaller
import random

class FollowUsers:


    def start(self, username, password, mode):
        chromedriver_autoinstaller.install() 
        driver = webdriver.Chrome()
        #region Login to Instagram
        driver.get("https://instagram.com")
        sleep(5)
        follow_limit = 200
        counter = 0
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

        #region RabbitMQ Connection
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        if mode == "hashtag":
            channel.queue_declare(queue='hashtag-queue', durable=True)
        elif mode == "followed":
            channel.queue_declare(queue='durable-queue', durable=True)
        elif mode == "followers":
            channel.queue_declare(queue='durable-queue', durable=True)
        #endregion RabbitMQ Connection

        #region Go to profiles and follow them
        def follow(user):
            user_link = "https://www.instagram.com/" + user
            profile = driver.get(user_link)
            try:
                follow = driver.find_element_by_xpath("//*[text()='Takip Et']").click()
                
            except Exception as ex:
                print("User can't be follow! | ", ex)

            sleep(random.randint(5,15))
            driver.get("https://instagram.com")
            sleep(random.randint(3,8))
        #endregion Go to profiles and follow them

        #region Get username from the queue

        def callback(ch, method, properties, body):
            print(f"Recieved a username from the queue: {body.decode()}")
         
            follow(body.decode())

            ch.basic_ack(delivery_tag = method.delivery_tag)

        #endregion Get username from the queue

        channel.basic_qos(prefetch_count=1)
        
        if counter >= follow_limit:
                print("Shutting down..")
                print(quit)
                quit()
                
        if mode == "hashtag":
            channel.basic_consume(queue='hashtag-queue',
                        on_message_callback=callback)
            counter = counter + 1
        elif mode == "followed":
            channel.basic_consume(queue='durable-queue',
                        on_message_callback=callback)
        elif mode == "followers":
            channel.basic_consume(queue='durable-queue',
                        on_message_callback=callback)

        print('Waiting for usernames.. Press CTRL+C to quit.')
        channel.start_consuming()





