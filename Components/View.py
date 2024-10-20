#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
__Author__ = 'Kayuã Oleques'
__GitPage__ = 'unknown@unknown.com.br'
__version__ = '{1}.{0}.{0}'
__initial_data__ = '2024/10/20'
__last_update__ = '2024/10/22'
__credits__ = ['INF-UFRGS']


try:
    import sys
    from pyfiglet import Figlet

except ImportError as error:

    print(error)
    print()
    print("1. (optional) Setup a virtual environment: ")
    print("  python3 - m venv ~/Python3env/ReliableCommunication ")
    print("  source ~/Python3env/DroidAugmentor/bin/activate ")
    print()
    print("2. Install requirements:")
    print("  pip3 install --upgrade pip")
    print("  pip3 install -r requirements.txt ")
    print()
    sys.exit(-1)

class View:
    """
    Class responsible for rendering a visual representation of the server title using ASCII art.
    """

    def __init__(self, title='Reliable Communication'):
        """
        Initializes the view with a given title.

        Args:
            title (str): The title to be displayed.
        """
        self.title = title

    def print_view(self, mode):
        """
        Renders and prints the title using the 'slant' font from pyfiglet.
        Also prints a smaller secondary text below it using the 'mini' font.
        """
        font_tex = Figlet(font='slant')
        print(font_tex.renderText(self.title))

        # Adding the smaller text
        small_text = mode
        f_small = Figlet(font='mini')
        print(f_small.renderText(small_text))
        print("-"*30)
