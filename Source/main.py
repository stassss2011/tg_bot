class Manager:
    def __init__(self):
        self.image_obj = None
        self.filter_chain = None
        print("Created Manager")

    def open_file(self, file_name):
        self.image_obj = Image(file_name)

    def save_file(self):
        pass

    def init_filter_chain(self):
        self.filter_chain = FilterChain()

    def add_filter_to_chain(self, f_id):
        if self.filter_chain is None:
            self.init_filter_chain()
        self.filter_chain.add(f_id)

    def delete_filter_from_chain(self):
        self.filter_chain.delete()

    def apply_filter_chain(self):
        self.filter_chain.apply(self.image_obj)


class Image:
    def __init__(self, file_name):
        print("Created Image")
        with open(file_name, "r") as file_obj:
            self.image = file_obj.read()


class FilterChain:
    chain = []

    def __init__(self):
        print("Created FilterChain")

    def add(self, f_id):
        self.chain.append(f_id)

    def delete(self):
        self.chain.clear()

    def apply(self, image):
        for i in range(len(self.chain)):
            Filter(image, self.chain[i])


class Filter:
    def __init__(self, image, f_id):
        print("Created Filter")
        self.image = image
        self.f_id = f_id


mng = Manager()
print("opening file")
mng.open_file("img.txt")
print("add filter to chain")
mng.add_filter_to_chain(5)
print("add filter to chain")
mng.add_filter_to_chain(3)
print("add filter to chain")
mng.add_filter_to_chain(6)
print("apply filter")
mng.apply_filter_chain()
print("delete filter chain")
mng.delete_filter_from_chain()
print("save file")
mng.save_file()
