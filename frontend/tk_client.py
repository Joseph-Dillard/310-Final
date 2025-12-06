import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from frontend.ui import App


def main():
    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()
