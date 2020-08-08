

import conf1, json, time, math, statistics,requests
from boltiot import Sms, Bolt
def compute_bounds(history_data,frame_size,factor):
    if len(history_data)<frame_size :
        return None

    if len(history_data)>frame_size :
        del history_data[0:len(history_data)-frame_size]
    Mn=statistics.mean(history_data)
    Variance=0
    for data in history_data :
        Variance += math.pow((data-Mn),2)
    Zn = factor * math.sqrt(Variance / frame_size)
    High_bound = history_data[frame_size-1]+Zn
    Low_bound = history_data[frame_size-1]-Zn
    return [High_bound,Low_bound]

minimum_limit =200
maximum_limit =250
#mybolt = Bolt(conf.API_KEY, conf.DEVICE_ID)
mybolt = Bolt(conf1.bolt_api_key, conf1.device_id)

#sms = Sms(conf.SSID, conf.AUTH_TOKEN, conf.TO_NUMBER, conf.FROM_NUMBER)

history_data=[]
startTime = time.time()    # get the first lap's start time
lastTime = startTime
lapNum = 1
'''
def get_sensor_value_from_pin(pin):
    """Returns the sensor value. Returns -999 if request fails"""
    try:
        response = mybolt.analogRead(pin)
        data = json.loads(response)
        if data["success"] != 1:
            print("Request not successfull")
            print("This is the response->", data)
            return -999
        sensor_value = int(data["value"])
        return sensor_value
    except Exception as e:
        print("Something went wrong when returning the sensor value")
        print(e)
        return -999
'''

def send_telegram_message(message):
    """Sends message via Telegram"""
    url = "https://api.telegram.org/" + conf1.telegram_bot_id + "/sendMessage"
    data = {
        "chat_id": conf1.telegram_chat_id,
        "text": message
    }
    try:
        response = requests.request(
            "GET",
            url,
            params=data
        )
        print("This is the Telegram response")
        print(response.text)
        telegram_data = json.loads(response.text)
        return telegram_data["ok"]
    except Exception as e:
        print("An error occurred in sending the alert message via Telegram")
        print(e)
        return False


while True:
   # print ("Reading sensor value")
    response = mybolt.analogRead('A0')
    data = json.loads(response)
   # print("Sensor value is: " + str(data['value']))
    if data['success'] != 1:
        print("There was an error while retriving the data.")
        print("This is the error:"+data['value'])
        time.sleep(10)
        continue

    print ("This is the value "+data['value'])
    sensor_value=0
    try:
        sensor_value = int(data['value'])
    except e:
        print("There was an error while parsing the response: ",e)
        continue

    bound = compute_bounds(history_data,conf.FRAME_SIZE,conf.MUL_FACTOR)
    if not bound:
        required_data_count=conf.FRAME_SIZE-len(history_data)
        print("Not enough data to compute Z-score. Need ",required_data_count," more data points")
        history_data.append(int(data['value']))
        time.sleep(2)
        continue

    try:
        if sensor_value > bound[0] :
           # print ("The temperature level increased suddenly. Sending an SMS.")
            message = "The temperature level increased suddenly than " + str(conf1.threshold) + \
                  ". The current value is " +str(sensor_value)
            telegram_status = send_telegram_message(message)
            print("This is the Telegram status:", telegram_status)

	   # response = sms.send_sms("Someone has opened the fridge")
           # print("This is the response ",response)
        elif sensor_value < bound[1]:
           # print ("The temperature level decreased suddenly. Sending an SMS.")
             message = "The temperature level decreased suddenly than " + str(conf1.threshold) + \
                  ". The current value is " +str(sensor_value)
             telegram_status = send_telegram_message(message)
             print("This is the Telegram status:", telegram_status)

            #response = sms.send_sms("Someone has closed the fridge")
            #print("This is the response ",response)
        history_data.append(sensor_value);
    except Exception as e:
        print ("Error",e)
    time.sleep(5)

    try:
        sensor_value = int(data['value'])
        if sensor_value > maximum_limit or sensor_value < minimum_limit:
           #print("The temperature has crossed threshold.Sending an SMS")
            message = "The temperature has crossed threshold which is " + str(conf1.threshold) + \
                  ". The current value is "+str(sensor_value)
            telegram_status = send_telegram_message(message)
            print("This is the Telegram status:", telegram_status)

	   # print("Making request to Twilio to send a SMS")
           # response = sms.send_sms("The Current temperature sensor value is " +str(sensor_value))
            #print("Response received from Twilio is: " + str(response))
            #print("Status of SMS at Twilio is :" + str(response.status))
        else:
            print("The temperature has not crossed threshold")
    except Exception as e:
        print ("Error occured: Below are the details")
        print (e)
    time.sleep(5)

    try:
       lapTime = round(time.time() - lastTime, 2)
       totalTime = round(time.time() - startTime, 2)

       lapNum += 1
       lastTime = time.time() # reset the last lap time
       ans=round(totalTime,2)
       print("The total time after doing Z-analysis is",ans)
       if ans>=120 and sensor_value>=200 and sensor_value<=300:
         #print("The temperature is between 200 to 300 for more than 2 minutes,Warning!.Sending an SMS")
          message = "The temperature is between 200 to 300 for more than 2 minutes,Warning!.Sending an SMS."  "The current value is "+str(sensor_value)
          telegram_status = send_telegram_message(message)
          print("This is the Telegram status:", telegram_status)

          #response = sms.send_sms("The Current temperature sensor value is " +str(sensor_value))
          #print("Response received from Twilio is: " + str(response))
          #print("Status of SMS at Twilio is :" + str(response.status))
       elif ans>=120:
         # print("The temperature is not between 200 and 300 after 2 minutes")
          message = "The temperature is not between 200 and 300 after 2 minutes.Sending an SMS."  " The current value is "+str(sensor_value)
          telegram_status = send_telegram_message(message)
          print("This is the Telegram status:", telegram_status)


    except KeyboardInterrupt:
       print('\nDone.')
    time.sleep(10)