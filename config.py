from cmu_graphics import rgb

#this file has all of the colors and settings for the game

DIFFICULTIES = {
    "Easy": (8, 10, 10),
    "Medium": (14, 18, 40),
    "Hard": (20, 24, 99),
    "Custom": (14, 18, 40)
}

NUMBER_COLORS = {
    1: (rgb(72, 133, 237), rgb(47, 86, 154)),   # Blue
    2: (rgb(0, 135, 68), rgb(0, 88, 44)),       # Green
    3: (rgb(219, 50, 54), rgb(142, 33, 35)),    # Red
    4: (rgb(182, 72, 242), rgb(118, 47, 157)),  # Purple
    5: (rgb(244, 132, 13), rgb(159, 86, 8)),    # Orange
    6: (rgb(72, 230, 241), rgb(47, 150, 157)),  # Cyan
    7: (rgb(237, 68, 181), rgb(154, 44, 118)),  # Pink
    8: (rgb(244, 194, 13), rgb(159, 126, 8))    # Yellow
}

TEXT_COLORS = {
    1: rgb(25, 118, 210),   # Blue
    2: rgb(56, 142, 60),    # Green
    3: rgb(211, 47, 47),    # Red
    4: rgb(123, 31, 162),   # Purple
    5: rgb(255, 143, 0),    # Orange
    6: rgb(0, 152, 165),    # Teal
    7: rgb(66, 66, 66),     # Dark Gray
    8: rgb(160, 159, 158)   # Light Gray
}
