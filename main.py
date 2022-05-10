import sys
from Config import Config
username = str(Config.GetConfig("Instagram", "username"))
password = str(Config.GetConfig("Instagram", "password"))

print("Username: ", username)
print("Password: ", password)

argumentList = sys.argv[1:]
if len(argumentList) > 0:

        if argumentList[0] == "FollowUsers":
            try:
                from Service.FollowUsers import FollowUsers
                mode = argumentList[1] #If there is a mod TODO
                #mode = int(argumentList[2]) #If there is a mod TODO
                followUsers = FollowUsers()
                followUsers.start(username = username, password = password, mode = mode)

            except Exception as ex:
                print("FollowUsers couldn't run! | ", ex)

        elif argumentList[0] == "UserDetectFromHashtag":
            try:
                from Service.UserDetectFromHashtag import UserDetectFromHashtag
                userDetectFromHashtag = UserDetectFromHashtag
                userDetectFromHashtag.start(username = username, password = password)

            except Exception as ex:
                print("UserDetectFromHashtag couldn't run! | ", ex) 
        else:
            print("Service not found")

else:
    print("Input <ServiceName> Parameter")
    from Service.UserDetectFromHashtag import UserDetectFromHashtag
    userDetectFromHashtag = UserDetectFromHashtag
    userDetectFromHashtag.start(username = username, password = password)