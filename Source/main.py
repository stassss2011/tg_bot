from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
from PIL import Image, ImageFilter, ImageEnhance


class Manager:
    def __init__(self):
        self.image_obj = None
        self.filter_chain = None
        print("Created Manager")

    def open_file(self, file_name):
        self.image_obj = Image.open("./" + str(file_name))
        self.image_obj.show()

    def save_file(self, out_name):
        self.image_obj.show()
        if str(out_name)[-4] != '.':
            out_name = str(out_name) + ".png"
        self.image_obj.save("./" + str(out_name))

    def init_filter_chain(self):
        self.filter_chain = FilterGroup()

    def add_filter_to_chain(self, f_id, *args):
        if self.filter_chain is None:
            self.init_filter_chain()
        if isinstance(args[0], list):
            self.filter_chain.add(Filter(f_id, args[0]))
        else:
            self.filter_chain.add(Filter(f_id, args))

    def remove_filter_from_chain(self):
        self.filter_chain.remove()

    def apply_filter_chain(self):
        if self.filter_chain is not None:
            self.image_obj = self.filter_chain.apply(self.image_obj)

    def save_complex_filter(self):
        if self.filter_chain is not None:
            file = open("filter.txt", "w")
            file.write(self.filter_chain.get_filter_list())
            file.close()

    def load_complex_filter(self, file_name):
        file = open(file_name, "r")
        operations = file.read().split("\n")
        for oper_str in operations:
            oper_list = oper_str.split()
            if oper_list:
                f_id = oper_list[0]
                if len(oper_list) > 1:
                    args = oper_list[1:]
                else:
                    args = None
                self.add_filter_to_chain(f_id, args)


class FilterInterface(ABC):
    @property
    def parent(self) -> FilterInterface:
        return self._parent

    @parent.setter
    def parent(self, parent: FilterInterface):
        self._parent = parent

    def add(self, component: FilterInterface) -> None:
        pass

    def remove(self) -> None:
        pass

    def is_composite(self) -> bool:
        return False

    @abstractmethod
    def apply(self, image):
        pass

    @abstractmethod
    def get_filter_list(self):
        pass


class Filter(FilterInterface):
    def __init__(self, f_id, args):
        print("Created Filter-class")
        self.args = args
        self.name = str(f_id)

    def get_filter_list(self) -> str:
        return str(self.name) + ' ' + str(' '.join(map(str, list(self.args))))

    def apply(self, image) -> Image:
        if self.name == "blur":
            return image.filter(ImageFilter.GaussianBlur(int(self.args[0])))
        elif self.name == "boxblur":
            return image.filter(ImageFilter.BoxBlur(int(self.args[0])))
        elif self.name == "rotate":
            return image.rotate(float(self.args[0]))
        elif self.name == "resize":
            return image.resize((int(self.args[0]), int(self.args[1])))
        elif self.name == "flip":
            if self.args[0] == "v":
                return image.transpose(Image.FLIP_LEFT_RIGHT)
            elif self.args[0] == "h":
                return image.transpose(Image.FLIP_TOP_BOTTOM)
        elif self.name == "color":
            return ImageEnhance.Color(image).enhance(float(self.args[0]))
        elif self.name == "contrast":
            return ImageEnhance.Contrast(image).enhance(float(self.args[0]))
        elif self.name == "brightness":
            return ImageEnhance.Brightness(image).enhance(float(self.args[0]))
        elif self.name == "sharpness":
            return ImageEnhance.Sharpness(image).enhance(float(self.args[0]))
        else:
            return image


class FilterGroup(FilterInterface):
    def __init__(self):
        print("Created filter group-class")
        self.image = None
        self._children: List[FilterInterface] = []

    def add(self, component: FilterInterface) -> None:
        self._children.append(component)
        component.parent = self

    def remove(self) -> None:
        self._children[-1].parent = None
        self._children.pop()

    def is_composite(self) -> bool:
        return True

    def get_filter_list(self) -> str:
        f_list = str()
        if len(self._children) != 0:
            for child in self._children:
                f_list += str(child.get_filter_list() + "\n")
            return f_list
        else:
            return ""

    def apply(self, image) -> Image:
        self.image = image
        for child in self._children:
            self.image = child.apply(self.image)
        return self.image


MNG = Manager()
print("opening file")
MNG.open_file("test.png")



# print("add filter to chain")
# mng.add_filter_to_chain("rotate", 30)
# print("add filter to chain")
MNG.add_filter_to_chain("resize", 700, 700)
# MNG.add_filter_to_chain("flip", "v")
# MNG.add_filter_to_chain("flip", "h")
# MNG.add_filter_to_chain("color", 1.5)
# MNG.add_filter_to_chain("contrast", 1.5)
# MNG.add_filter_to_chain("brightness", 1.5)
MNG.add_filter_to_chain("sharpness", 30)
MNG.add_filter_to_chain("blur", 3)


MNG.save_complex_filter()

print("load_filters")
# MNG.load_complex_filter("filter.txt")

# MNG.remove_filter_from_chain()

# MNG.add_filter_to_chain("boxblur", 3)

print("apply filter")
MNG.apply_filter_chain()

print("save file")
MNG.save_file("out.jpg")
