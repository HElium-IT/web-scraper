from bs4.element import PageElement

class Item:
    """abc"""
    def __init__(self) -> None:
        pass

    def set_bs4_element(self, element: PageElement) -> None:
        self.element = element
    