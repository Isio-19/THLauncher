import os 
import re
import requests
import threading

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap

from icoextract import IconExtractor, IconExtractorError

from io import BytesIO

from PIL import Image

from itertools import compress


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Touhou Launcher")
        self.setGeometry(QRect(0, 0, 1000, 540))
        
        layout = QGridLayout()
        # TODO: make the scroll work
        self.widget = QScrollArea()
        self.widget.setLayout(layout)
        self.widget.setWidgetResizable(False)
        self.setCentralWidget(self.widget)

    def addWidget(self, widget, x, y):
        self.widget.layout().addWidget(widget, x, y)

def filterFolder(input_text):
    pattern = re.compile(r"[A-Za-z]+ [0-9]+", re.IGNORECASE)
    return bool(re.search(pattern, input_text))

def findExe(folder):
    pattern = re.compile(r"^(Touhou|th|game)([0-9]*)?\.exe", re.IGNORECASE)
    
    for file in next(iter(os.walk(folder)))[2]:
        if pattern.match(file):
            return file
    return FileNotFoundError

def fetchImage(number):
    img = None
    for format in [".png", ".jpg"]:
        for typeImg in ["cover", "front"]:
            r=requests.get(
                f"https://en.touhouwiki.net/wiki/Special:Redirect/file/Th{number}{typeImg}{format}", 
                headers={'User-agent': 'Mozilla/5.0'}, 
            )
            if r.status_code == 200: 
                if img != None:
                    # download the image that is closed to a square
                    tmp = Image.open(BytesIO(r.content)) 
                    tmp_ratio = abs(1 - tmp.size[0]/tmp.size[1])
                    img_ratio = abs(1 - img.size[0]/img.size[1])

                    if img_ratio > tmp_ratio:
                        img = tmp
                    continue

                img = Image.open(BytesIO(r.content))
                
    img.save(f"img/th{number}.png")

if __name__ == "__main__":
    path = "D:\\Program Files\\Touhou\\Games"
    # TODO: make the user input this path

    # get every folders (games) in the path 
    games = os.listdir(path)
    mask = [filterFolder(game) for game in games]
    games = {
        el: {
            "number": float(el.split(" ")[1]),
            "name": el.split(" - ")[1] 
        }
        for el in compress(games, mask)
    }
    games = dict(
        sorted(games.items(), key=lambda item: item[1]["number"])
    )


    # format the number and find the exe location
    for key, value in games.items():
        number = value["number"]

        temp_number = str(number).replace(".", "")
        if number % 1 == 0: temp_number = str(int(number))
        if number < 10: temp_number = "0" + temp_number

        value["number"] = temp_number
        
        # find the exe
        location = ""
        try :
            exeName = findExe(f"{path}/{key}")
            value["location"] = f"{path}/{key}/{exeName}"
        except FileNotFoundError:
            value["location"] = "FileNotFound"
            pass
        
    # get the icon and image for each game executable
    for key, value in games.items():
        try:
            if value["location"] == "FileNotFound": 
                value["icon"] = "FileNotFound.ico"
                pass
            
            exe = value["location"]
            extractor = IconExtractor(value["location"])
            data = extractor.get_icon(num=0)
            im = Image.open(data)
            value["icon"] = im
            value["img"] = f"https://en.touhouwiki.net/wiki/Special:Redirect/file/Th{value['number']}cover"

        except IconExtractorError:
            pass
        
    # launch a window that let's you choose the game
        # show icon
        # show game title
        # show description?

    app = QApplication([])

    window = MainWindow()

    for index, (key, value) in enumerate(games.items()):
        print(key)
        # button to launch the game
        # TODO: launch exe
        button = QPushButton()
        button.setText("Launch Game")
        
        # image of the game cover
        img_label = QLabel()
       

        url = value["img"]
        image_name = f"th{value['number']}.png"
        if not (image_name in os.listdir("img/")):
            fetchImage(value['number'])
        img = QPixmap(f"img/{image_name}")
        img_label.setPixmap(img)
        # TODO: make the images responsive

        # add the widgets to the window
        window.addWidget(img_label, index, 0)
        window.addWidget(button, index, 1)
        window.addWidget(QLabel(key), index, 2)
        pass

    window.show()

    app.exec()

    # close the window when a game if chosen


    # reopen the window once the game is closed

# TODO: use thread for the image download