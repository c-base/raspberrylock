from gpiozero import Button, LED
from time import sleep

ROWS = [LED(17), LED(4), LED(3), LED(2)]
COLS = [Button(23, pull_up=False), Button(18, pull_up=False), Button(15, pull_up=False) , Button(14, pull_up=False)]


def one():
    while True:
        try:
            for out in ROWS:
                out.on()
                for pin in COLS:
                    print(pin.value)
                out.off()
                sleep(0.1)
        except:
            break

def two():

    for out in ROWS:
        out.on()

    for pin in COLS:
        pin.when_pressed = lambda: print("pressed")

    while True:
        pass


if __name__ == "__main__":

    two()    

    red = LED(26)

    while True:
        red.on()
        sleep(1)
        red.off()
        sleep(1)
