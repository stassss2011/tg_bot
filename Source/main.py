from __future__ import annotations
from PIL import Image, ImageFilter
from abc import ABC, abstractmethod
from typing import List


class Manager:
    def __init__(self):
        self.image_obj = None
        self.filter_chain = None
        print("Created Manager")

    def open_file(self, file_name):
        self.image_obj = Image.open("./" + str(file_name))
        self.image_obj.show()

    def save_file(self):
        self.image_obj.show()
        self.image_obj.save("./output.jpg")

    def init_filter_chain(self):
        self.filter_chain = FilterGroup()

    def add_filter_to_chain(self, f_id, *args):
        if self.filter_chain is None:
            self.init_filter_chain()
        if f_id == "blur":
            self.filter_chain.add(FilterBlur(args))

    def remove_filter_from_chain(self):
        # self.filter_chain.remove()
        pass

    def apply_filter_chain(self):
        self.image_obj = self.filter_chain.apply(self.image_obj)


class FilterInterface(ABC):
    @property
    def parent(self) -> FilterInterface:
        return self._parent

    @parent.setter
    def parent(self, parent: FilterInterface):
        self._parent = parent

    def add(self, component: FilterInterface) -> None:
        pass

    def remove(self, component: FilterInterface) -> None:
        pass

    def is_composite(self) -> bool:
        return False

    @abstractmethod
    def apply(self, image):
        pass


class Filter(FilterInterface, ABC):
    def __init__(self, *args):
        print("Created Filter")
        self.image = None
        self.args = args


class FilterBlur(Filter):
    def apply(self, image):
        self.image = image
        self.image = self.image.transpose(Image.ROTATE_90).filter(ImageFilter.BLUR)
        return self.image


class FilterGroup(FilterInterface):
    def __init__(self):
        print("Created filter group")
        self.image = None
        self._children: List[FilterInterface] = []

    def add(self, component: FilterInterface) -> None:
        self._children.append(component)
        component.parent = self

    def remove(self, component: FilterInterface) -> None:
        self._children.remove(component)
        component.parent = None

    def is_composite(self) -> bool:
        return True

    def apply(self, image):
        self.image = image
        for child in self._children:
            self.image = child.apply(self.image)
        return self.image


mng = Manager()
print("opening file")
mng.open_file("test.png")
print("add filter to chain")
mng.add_filter_to_chain("blur", 3)
print("add filter to chain")
mng.add_filter_to_chain("blur", 3)
print("add filter to chain")
mng.add_filter_to_chain("blur", 3)
print("apply filter")
mng.apply_filter_chain()
print("save file")
mng.save_file()
