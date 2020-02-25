from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from time import sleep
import numpy as np
import Account
from math import exp
from twilio.rest import Client

max_available_hours = 4
preferred_start_time = int(input("Enter preferred start time (hh): ")) - 9
reservation_name = input("Enter name of reservation: ")
date = input("Enter date of reservation (MMDD): ")

#Twilio code is commented out since you have to generate tokens and phone numbers to use it
# account_sid = '<Twilio sid>'
# auth_token = '<Twilio token>'
# client = Client(account_sid, auth_token)


browser = webdriver.Chrome()

browser.get('https://daisy.dsv.su.se/index.jspa')
sleep(1)


su_button = browser.find_element_by_xpath('//*[@id="login"]/div[1]/div/a[1]')
su_button.click()

sleep(1)

username_field = browser.find_element_by_xpath('//*[@id="username"]')
username_field.send_keys(Account.name)

pw_field = browser.find_element_by_xpath('//*[@id="password"]')
pw_field.send_keys(Account.password)

login_button = browser.find_element_by_xpath('//*[@id="login"]/div[1]/div[3]/div[2]/button')
login_button.click()

sleep(4)

schedule_button = browser.find_element_by_xpath('//*[@id="menyflikar"]/li[3]/a')
schedule_button.click()

local_link = browser.find_element_by_xpath('//*[@id="momentmeny"]/tbody/tr/td[2]/a')
local_link.click()

month_button = Select(browser.find_element_by_xpath('//*[@id="body"]/form[1]/table/tbody/tr[2]/td[4]/select'))
month_button.select_by_value(date[0:2])

day_button = Select(browser.find_element_by_xpath('//*[@id="body"]/form[1]/table/tbody/tr[2]/td[6]/select'))
day_button.select_by_value(date[2:])

display_date_button = browser.find_element_by_xpath('//*[@id="body"]/form[1]/table/tbody/tr[2]/td[7]/input')
display_date_button.click()

#Columns represent rooms, rows represents hours. 0 = not booked, 1 = booked
bookings = np.zeros(264, dtype=int)
bookings.shape = (11,24)



#Columns start at 2 and end at 25, rows start at 3 and end at 13
min_col = 2
max_col = 26

min_row = 3
max_row = 14
    
#Translate occupied rooms to matrix
for y in range(max_row - min_row):
    occupied_counter = 0
    for x in range(max_col - min_col):
        try:
            if bookings[y][x] == 0:

                cell_path = '//*[@id="body"]/table/tbody/tr[' + str(y+min_row) + ']/td[' + str(x+min_col - occupied_counter) + ']'
                cell = browser.find_element_by_xpath(cell_path)
                cell_color = cell.get_attribute('bgcolor')

                #Check how many rows are covered
                if cell_color == '#e7f1ff':
                    booked_hours = int(cell.get_attribute('rowspan'))
                    for i in range(booked_hours):
                        bookings[y+i][x] = 1

            else:
                occupied_counter += 1

        except:
           pass




#Find best available fit key = first position of best fit, value = length of best fit
best_fit = [0,0]
best_fit_length = 0

for y in range(len(bookings)):
    for x in range(len(bookings[y])):
        if bookings[y][x] == 0:
            available_count = 0
            i = 0
            try:
                while bookings[y + i][x] != 1 and i < max_available_hours:
                    available_count += 1
                    i += 1
            except:
                pass
        
            if available_count - int(exp(abs(preferred_start_time - y)) * 0.1) > best_fit_length:
                best_fit = [y,x]
                best_fit_length = available_count




reservation_button = browser.find_element_by_xpath('//*[@id="body"]/form[2]/input[2]')
reservation_button.click()

base_window = browser.window_handles[0]
popup = browser.window_handles[1]

browser.switch_to.window(popup)

title_field = browser.find_element_by_xpath('//*[@id="bokning_namn"]')
title_field.send_keys(reservation_name)

start_time_field = Select(browser.find_element_by_xpath('//*[@id="bokning_from"]'))
start_time_field.select_by_index(3 + best_fit[0])

end_time_field = Select(browser.find_element_by_xpath('//*[@id="bokning_to"]'))
end_time_field.select_by_index(3 + best_fit[0] + best_fit_length)

room = Select(browser.find_element_by_xpath('//*[@id="bokning_lokalID"]'))
room.select_by_index(best_fit[1])
room_name = room.first_selected_option.text

collegue_field = browser.find_element_by_xpath('//*[@id="selectbokning"]')
collegue_field.send_keys(Account.other_student + Keys.RETURN)
sleep(4)
collegue_field.send_keys(Keys.RETURN)


confirm_button = browser.find_element_by_xpath('//*[@id="submitBtn"]')
confirm_button.click()


print("Booked room: " + room_name + " between " + str(9 + best_fit[0]) + ":00 - " + str(9 + best_fit[0] + best_fit_length) + ":00 on " + date[2:] + "/" + date[0:2])


# message = client.messages.create(

#     to=Account.phone_number,
#     from_="<Phone number that is generated on Twilio webpage>",
#     body="Booked room: " + room_name + " between " + str(9 + best_fit[0]) + ":00 - " + str(9 + best_fit[0] + best_fit_length) + ":00 on " + date[2:] + "/" + date[0:2]

# )



browser.close()
browser.switch_to.window(base_window)
browser.refresh()
browser.close()