import sys
import os
try:
    print("frozen:", getattr(sys, 'frozen', False))
    print("_MEIPASS exists:", hasattr(sys, '_MEIPASS'))
    if hasattr(sys, '_MEIPASS'):
        print("_MEIPASS:", sys._MEIPASS)
except Exception as e:
    print(e)
