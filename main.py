import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QLabel
# from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtGui import QIcon, QPixmap
import random
from PIL import Image, ImageDraw


class ImageForm(QtWidgets.QWidget):
    WIDTH = 150
    HEIGHT = 150

    def __init__(self, parent=None, image="_hello_.jpg"):
        super().__init__(parent)
        uic.loadUi("ImageForm.ui", self)
        self.image_file_name = image
        self.file_name = image.split(".")[0]
        self.size = (self.WIDTH, self.HEIGHT)
        self.label = QLabel(self)
        self._run()

    def _run(self):
        self.pushButtonReset.clicked.connect(self._reset)
        self.horizontalSliderResizeW.valueChanged.connect(self._resize_image)
        self.verticalSliderResizeH.valueChanged.connect(self._resize_image)
        self.horizontalSliderDepth.valueChanged.connect(self._change_image)
        self.horizontalSliderNoise.valueChanged.connect(self._change_image)
        self.horizontalSliderBrightness.valueChanged.connect(self._change_image)
        self.horizontalSliderMonochrome.valueChanged.connect(self._change_image)

        image = Image.open(self.image_file_name)
        self._load_image(image, self.file_name)
        self.label.move((self.width() - self.image.width()) // 2, (self.height() - self.image.height() - 130) // 2)

    def _load_image(self, image, file_name):
        image = self.crop(image, self.size)
        image.putalpha(self.prepare_mask(self.size, 4))
        image.save(f"{file_name}.png")
        self.image = QPixmap(f"{file_name}.png")
        self.label.setPixmap(self.image)

    def _reset(self):
        self.horizontalSliderDepth.setValue(0)
        self.horizontalSliderNoise.setValue(0)
        self.horizontalSliderBrightness.setValue(0)
        self.horizontalSliderMonochrome.setValue(0)

    def _set_text(self, text_obj, value):
        text_obj.setText(str(value))

    def _resize_image(self):
        width_value = self.horizontalSliderResizeW.value()
        height_value = self.verticalSliderResizeH.value()
        image = Image.open(self.image_file_name)

        if width_value != 0:
            crop_value = image.size[0] * (abs(50 - width_value) * 2 / 100)
            if image.size[0] - crop_value >= self.size[0]:
                if width_value < 50:
                    image = image.crop((0, 0, image.size[0] - crop_value, image.size[1]))
                elif width_value > 50:
                    image = image.crop((crop_value, 0, image.size[0], image.size[1]))

        if height_value != 0:
            crop_value = image.size[1] * (abs(50 - height_value) * 2 / 100)
            if image.size[1] - crop_value >= self.size[0]:
                if height_value < 50:
                    image = image.crop((0, 0, image.size[0], image.size[1] - crop_value))
                elif height_value > 50:
                    image = image.crop((0, crop_value, image.size[0], image.size[1]))
        self._load_image(image, self.file_name)

    @staticmethod
    def prepare_mask(size, antialias=2):
        mask = Image.new('L', (size[0] * antialias, size[1] * antialias), 0)
        ImageDraw.Draw(mask).ellipse((0, 0) + mask.size, fill=255)
        return mask.resize(size, Image.ANTIALIAS)

    @staticmethod
    def crop(im, s):
        w, h = im.size
        k = w / s[0] - h / s[1]
        if k > 0:
            im = im.crop(((w - h) / 2, 0, (w + h) / 2, h))
        elif k < 0:
            im = im.crop((0, (h - w) / 2, w, (h + w) / 2))
        return im.resize(s, Image.ANTIALIAS)

    def _change_image(self):
        image = Image.open(f"{self.file_name}.png")
        self._set_text(self.lineEditDepth, self.horizontalSliderDepth.value())
        image = self._depth(image, int(self.lineEditDepth.text()))
        self._set_text(self.lineEditNoise, self.horizontalSliderNoise.value())
        image = self._noise(image, int(self.lineEditNoise.text()))
        self._set_text(self.lineEditBrightness, self.horizontalSliderBrightness.value())
        image = self._brightness(image, int(self.lineEditBrightness.text()))
        self._set_text(self.lineEditMonochrome, self.horizontalSliderMonochrome.value())
        image = self._monochrome(image, int(self.lineEditMonochrome.text()))
        self._load_image(image, f"{self.file_name}_result")

    def _depth(self, image, value):
        # image = Image.open(f"{self.file_name}.png")
        image = image
        draw = ImageDraw.Draw(image)
        width = image.size[0]
        height = image.size[1]
        pix = image.load()

        depth = value
        if depth != 0:
            for i in range(width):
                for j in range(height):
                    a = pix[i, j][0]
                    b = pix[i, j][1]
                    c = pix[i, j][2]
                    s = (a + b + c) // 3
                    a = s + depth * 2
                    b = s + depth
                    c = s
                    if a > 255:
                        a = 255
                    if b > 255:
                        b = 255
                    if c > 255:
                        c = 255
                    draw.point((i, j), (a, b, c))
        # del draw
        return image

    def _noise(self, image, value):
        image = image
        draw = ImageDraw.Draw(image)
        width = image.size[0]
        height = image.size[1]
        pix = image.load()

        factor = value
        if factor != 0:
            for i in range(width):
                for j in range(height):
                    rand = random.randint(-factor, factor)
                    a = pix[i, j][0] + rand
                    b = pix[i, j][1] + rand
                    c = pix[i, j][2] + rand
                    if a < 0:
                        a = 0
                    if b < 0:
                        b = 0
                    if c < 0:
                        c = 0
                    if a > 255:
                        a = 255
                    if b > 255:
                        b = 255
                    if c > 255:
                        c = 255
                    draw.point((i, j), (a, b, c))
        # del draw
        return image

    def _brightness(self, image, value):
        image = image
        draw = ImageDraw.Draw(image)
        width = image.size[0]
        height = image.size[1]
        pix = image.load()

        factor = value
        if factor != 0:
            for i in range(width):
                for j in range(height):
                    a = pix[i, j][0] + factor
                    b = pix[i, j][1] + factor
                    c = pix[i, j][2] + factor
                    if a < 0:
                        a = 0
                    if b < 0:
                        b = 0
                    if c < 0:
                        c = 0
                    if a > 255:
                        a = 255
                    if b > 255:
                        b = 255
                    if c > 255:
                        c = 255
                    draw.point((i, j), (a, b, c))
        # del draw
        return image

    def _monochrome(self, image, value):
        image = image
        draw = ImageDraw.Draw(image)
        width = image.size[0]
        height = image.size[1]
        pix = image.load()

        factor = value
        if factor != 0:
            for i in range(width):
                for j in range(height):
                    a = pix[i, j][0]
                    b = pix[i, j][1]
                    c = pix[i, j][2]
                    s = a + b + c
                    if s > (((255 + factor) // 2) * 3):
                        a, b, c = 255, 255, 255
                    else:
                        a, b, c = 0, 0, 0
                    draw.point((i, j), (a, b, c))
        # del draw
        return image


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    progress = ImageForm()
    progress.show()
    sys.exit(app.exec_())
