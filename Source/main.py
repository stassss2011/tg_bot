# -*- coding: utf-8 -*-
from __future__ import annotations

from abc import ABC
from typing import List

from PIL import Image, ImageFilter, ImageEnhance


class Manager:
    def __init__(self):
        self.image_obj = None
        self.filter_chain = None
        self.image_copy = None

    def open_file(self, file_name):
        self.image_obj = Image.open(file_name)
        self.image_copy = self.image_obj

    def save_file(self, file_name):
        if self.image_obj is not None:
            self.image_obj.save(file_name)

    def init_filter_chain(self):
        self.filter_chain = FilterGroup()

    def add_filter_to_chain(self, f_id, *args):
        if self.filter_chain is None:
            self.init_filter_chain()
        filter_list = {
            "blur": Blur,
            "boxblur": BoxBlur,
            "rotate": Rotate,
            "resize": Resize,
            "flip": Flip,
            "color": AdjustColor,
            "contrast": AdjustContrast,
            "brightness": AdjustBrightness,
            "sharpness": AdjustSharpness}
        filter_i = filter_list.get(f_id, None)
        if isinstance(args[0], list):
            args = args[0]
        self.filter_chain.add(filter_i(args))

    def remove_filter_from_chain(self):
        if self.filter_chain is not None:
            self.filter_chain.remove()

    def apply_filter_chain(self):
        if self.filter_chain is not None:
            self.image_obj = self.filter_chain.apply(self.image_obj)

    def save_complex_filter(self, file_name):
        if self.filter_chain is not None:
            file = open(file_name, "w")
            file.write(self.get_filter_list())
            file.close()

    def get_filter_list(self):
        if self.filter_chain is not None:
            return self.filter_chain.get_filter_list()

    def load_complex_filter(self, file_name):
        file = open(file_name, "r")
        operations = file.read().split("\n")
        for oper_str in operations:
            self.add_filter_from_str(oper_str)

    def load_complex_filter_from_str(self, operations):
        for oper_str in operations.split("\n"):
            self.add_filter_from_str(oper_str)

    def add_filter_from_str(self, filter_str):
        filter_str = filter_str.split()
        if filter_str:
            f_id = filter_str[0]
            if len(filter_str) > 1:
                args = filter_str[1:]
            else:
                args = None
            self.add_filter_to_chain(f_id, args)

    def img_show(self):
        if self.image_obj is not None:
            self.image_obj.show()

    def reset(self):
        self.image_obj = self.image_copy


class FilterInterface(ABC):
    @property
    def parent(self) -> FilterInterface:
        return self._parent

    @parent.setter
    def parent(self, parent: FilterInterface):
        self._parent = parent

    def add(self, component: FilterInterface):
        pass

    def remove(self):
        pass

    def apply(self, image):
        pass

    def get_filter_list(self):
        pass


class Filter(FilterInterface, ABC):
    name: str

    def __init__(self, args):
        self.args = args

    def get_filter_list(self) -> str:
        return str(self.name) + ' ' + str(' '.join(map(str, list(self.args))))

    def apply(self, image):
        pass


class Blur(Filter):
    name = "blur"

    def apply(self, image) -> Image:
        return image.filter(ImageFilter.GaussianBlur(float(self.args[0])))


class BoxBlur(Filter):
    name = "boxblur"

    def apply(self, image) -> Image:
        return image.filter(ImageFilter.BoxBlur(float(self.args[0])))


class Rotate(Filter):
    name = "rotate"

    def apply(self, image) -> Image:
        return image.rotate(float(self.args[0]))


class Resize(Filter):
    name = "resize"

    def apply(self, image) -> Image:
        return image.resize((int(self.args[0]), int(self.args[1])))


class Flip(Filter):
    name = "flip"

    def apply(self, image) -> Image:
        mode = {
            "h": Image.FLIP_TOP_BOTTOM,
            "H": Image.FLIP_TOP_BOTTOM,
            "v": Image.FLIP_LEFT_RIGHT,
            "V": Image.FLIP_LEFT_RIGHT
        }
        return image.transpose(mode.get(self.args[0]))


class AdjustColor(Filter):
    name = "color"

    def apply(self, image) -> Image:
        return ImageEnhance.Color(image).enhance(float(self.args[0]))


class AdjustContrast(Filter):
    name = "contrast"

    def apply(self, image) -> Image:
        return ImageEnhance.Contrast(image).enhance(float(self.args[0]))


class AdjustBrightness(Filter):
    name = "brightness"

    def apply(self, image) -> Image:
        return ImageEnhance.Brightness(image).enhance(float(self.args[0]))


class AdjustSharpness(Filter):
    name = "sharpness"

    def apply(self, image) -> Image:
        return ImageEnhance.Sharpness(image).enhance(float(self.args[0]))


class FilterGroup(FilterInterface):
    def __init__(self):
        # print("Created filter group-class")
        self.image = None
        self._children: List[FilterInterface] = []

    def add(self, component: FilterInterface):
        self._children.append(component)
        component.parent = self

    def remove(self):
        if len(self._children) >= 1:
            self._children[-1].parent = None
            self._children.pop()

    def get_filter_list(self) -> str:
        f_list = str()
        if len(self._children) != 0:
            for child in self._children:
                f_list += str(child.get_filter_list() + "\n")
            return f_list
        return ""

    def apply(self, image) -> Image:
        self.image = image
        for child in self._children:
            self.image = child.apply(self.image)
        return self.image

# MNG = Manager()
# print("opening file")
# MNG.open_file("test.png")
# MNG.img_show()
#
# MNG.add_filter_to_chain("rotate", -27)
# MNG.add_filter_to_chain("resize", 700, 700)
# MNG.add_filter_to_chain("flip", "v")
# MNG.add_filter_to_chain("flip", "h")
# MNG.add_filter_to_chain("color", 1.5)
# MNG.add_filter_to_chain("contrast", 1.5)
# MNG.add_filter_to_chain("brightness", 1.5)
# MNG.add_filter_to_chain("sharpness", -2)
# MNG.add_filter_to_chain("sharpness", 2)
# MNG.add_filter_to_chain("boxblur", 0.5)
# MNG.add_filter_to_chain("blur", 3)
#
#
# MNG.save_complex_filter("filter.txt")
#
# print("load_filters")
# MNG.load_complex_filter("filter.txt")
#
# MNG.remove_filter_from_chain()
#
#
#
# print("apply filter")
# MNG.apply_filter_chain()
#
# print("save file")
# MNG.img_show()
# MNG.save_file("out.jpg")
