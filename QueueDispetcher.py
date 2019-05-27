import datetime
from collections import OrderedDict
from threading import Thread, Event, Lock
from time import sleep, time

from ruamel import yaml

SETTINGS_FILE = "settings.yaml"


def get_settings(filename):
    with open(filename) as file:
        return yaml.safe_load(file)


class Dispatcher(object):
    def __init__(self, show_time: int, default_time: int, print_function):
        self.print = print_function
        self._l = Lock()
        self.show_time = show_time
        self.default_time = default_time
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
        return f"Nothing to show.. last showtime: {now.hour}:{now.minute}:{now.second}"

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
                    if 'expire' not in msg:
                        msg['expire'] = time() + self.default_time
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
        with self._l:
            self._d[msg['id']] = msg


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
