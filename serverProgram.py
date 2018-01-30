import threading

from serverFunctions import doApiCall, giveInstruction
import GUI



t1 = threading.Thread(target=GUI.runGui())
t2 = threading.Thread(target=doApiCall())
t3 = threading.Thread(target=giveInstruction(1,"192.168.42.3","192.168.42.1"))


t1.start()
t2.start()
t3.start()


t1.join()
t2.join()
t3.join()