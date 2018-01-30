import threading

import serverFunctions
import GUI



t1 = threading.Thread(target=serverFunctions.doApiCall)
t2 = threading.Thread(target=serverFunctions.giveInstruction,args=(1,"192.168.42.1"))
t3 = threading.Thread(target=GUI.runGui)


t1.start()
t2.start()
t3.start()


t1.join()
t2.join()
t3.join()
