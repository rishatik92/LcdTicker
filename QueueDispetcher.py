import datetime
from collections import OrderedDict
from threading import Thread, Event, Lock
from time import sleep, time

from ruamel import yaml


class Dispatcher(object):
    """ Ticker dispatcher class."""

    MAX_SHOW_TIME = 86400 #seconds in one day

    def __init__(self, show_time: int, default_time: int, print_function, text_empty=None):
        self.print = print_function
        self._l = Lock()
        self.show_time = show_time
        self.default_time = default_time
        if not text_empty:
            text_empty = "Nothing to show."
        self.__text = text_empty
        self._d = OrderedDict()
        self.__stop = Event()
        self.__th = Thread(name="Dispatcher_thread", target=self.worker)
        self.__th.daemon = True
        self.__th.start()

    def close(self):
        self.__stop.set()

    def worker(self):
        while (not self.__stop.is_set()):
            self.print(self.get_message())
            sleep(self.show_time)

    def get_empty_msg(self):
        now = datetime.datetime.now()
        return f"{now.hour:02d}:{now.minute:02d}:{now.second:02d} {self.__text}"

    def get_message(self):
        """ Message format help """

        # the message is consist of next parts:
        #
        # 1. device identity
        # this identity must be unique in all queue, if new message with this identity will be received,
        # the lat message will be rewritten by message with this identity
        #
        # 2. ['expire'] time to expire, it must be posix time
        # if time of this message expired, the message must be deleted.
        #
        # 3. ['txt'] text
        # this text must be showed

        with self._l:
            result_msg = self.get_empty_msg()
            if self._d:
                key, msg = self._d.popitem(last=False)
                while True:  # iterate all expired messages

                    #First of all: looking to the 'expire' valur
                    try:
                        msg['expire'] = float(msg['expire'])
                    except Exception as ex:
                        print(f"unable to parse \"expire\" value: {ex}")
                        msg['expire'] = time() + self.default_time
                    finaly: # if incoming value is very big,  cut off
                        if msg['expire'] > time() + self.MAX_SHOW_TIME:
                            print(f"Time to show message: {msg} is very big, shorting to max time"}
                            msg['expire'] = time() + self.MAX_SHOW_TIME

                    if msg['expire'] < time():
                        del key, msg
                        if self._d:
                            key, msg = self._d.popitem(last=False)
                        else:
                            break
                    else:
                        self._d[key] = msg
                        result_msg =  msg['txt']
                        break
            return result_msg

    def put_message(self, msg):
        """ Add message to queue, message must to consist keys: id, txt. """

        with self._l:
            self._d[msg['id']] = msg



SETTINGS_FILE = "settings.yaml"
def get_settings(filename):
    with open(filename) as file:
        return yaml.safe_load(file)

def main():
    """simple scenario working"""

    settings = get_settings(SETTINGS_FILE)
    show_time = settings["show_time"]
    default_time = settings["default_time"]
    my_worker = Dispatcher(show_time, default_time, print)
    sleep(3)
    my_worker.put_message({"expire":time()+5, "id":"USDRUB", "txt":"USD/RUB -64.466"})
    my_worker.put_message({"expire": time() + 12, "id": "AAPL", "txt": "APPLE +70.11"})
    my_worker.put_message({"expire": time() + 46, "id": "GOOGL", "txt": "AlphaaBet +1005.16"})
    my_worker.put_message({"expire": time() + 6, "id": "FB", "txt": "Facebook  -300.72"})
    sleep(3)
    my_worker.put_message({"expire": time() + 5, "id": "USDRUB", "txt": "USD/RUB +66.466"})
    sleep(3)
    my_worker.put_message({"expire": time() + 12, "id": "AAPL", "txt": "APPLE +71.06"})
    sleep(3)
    my_worker.put_message({"expire": time() + 12, "id": "AAPL", "txt": "APPLE +73.73"})
    sleep(3)
    my_worker.put_message({"id": "GOOGL", "txt": "AlphaaBet +1305.47"})
    sleep(3)
    my_worker.put_message({"expire": time() + 5, "id": "USDRUB", "txt": "USD/RUB +66.836"})
    sleep(20)
    my_worker.put_message({"expire": time() + 5, "id": "USDRUB", "txt": "USD/RUB -66.236"})
    sleep(40)


if __name__ == "__main__":
    main()
