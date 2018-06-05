from bs4 import BeautifulSoup as bs4
import datetime
import re

class APARTMENT:
    def __init__(self, html):
        self.html = html
        self.body = self.html.find_all('section', attrs={'id': 'postingbody'})
        self.sizeinfo = self.html.find('span', attrs={'class': 'housing'}) #.string

        self.INTERNETSCORES = {'A': [0, 'Google Fiber confirmed (-0)'],  # "Google fiber" found mentioned in description. Fantastic.
                               'B': [3, 'Only high-speed internet confirmed (-3)'], # "A" not qualified, but "High-speed internet" is found, which is typically Gfiber
                               'C': [10, 'No mention of internet type (-10)'] # Neither mentioned, and what kind of business person leaves that out?
        }

        # Price constraints are built into the CL query, but these heuristics are meant to get more granular
        self.PRICESCORES = {'A': [10, 'Price below $800/mo, might be bad (-10)'], # Price below 800 - maybe not terrible but probably not great
                            'B': [3, 'Price between $800-$900/mo (-3)'],  # Price >800, <900 - probably okay, still a little low
                            'C': [0, 'Price between $900 and $1100/mo (-0)'],  # Price >900, <1100 - Sweet spot
                            'D': [6, 'Price above $1100/mo (-6)']  # Price > 1100 - Starting to get spendy
        }

        self.ROOMSCORES = { 'A': [6, '2 Bedroom (-6)'], # 2br
                            'B': [0, '1 Bedroom (-0)'], # 1br
                            'C': [2, 'Studio (-2)'], # Studio
                            'D': [0, 'Unable to determine room count (-0)']# Unable to determine room count
        }

        self.SIZESCORES = { 'A': [8, 'Size < 300ft (-8)'], # below 300ft
                            'B': [4, 'Size 300-450ft (-4)'], # below 450ft
                            'C': [2, 'Size 450-600ft (-2)'], # below 600ft
                            'D': [1, 'Size 600-750ft (-1)'], # below 750ft
                            'E': [0, 'Size 750-900ft (-0)'], # below 900ft
                            'F': [0, 'Size either > 900ft or could not be determined (-0)'] # above 900ft or something went wrong
        }

        self.LAUNDRYSCORES = { 'A': [0, 'Laundry in unit (-0)'],
                               'B': [10, 'Shared laundry (-10)']
        }

        self.AUTOREJECT = [ '(?i)quality[\s-]?hill'
        ]

    def score(self):
        # Start with a perfect score, subtract from here
        # Because I'm so optimistic
        if self.__autoreject() == True:
            return 'R'
        else:
            score = 100
            score -= self.INTERNETSCORES[self.__internet()][0]
            score -= self.PRICESCORES[self.__price()][0]
            score -= self.SIZESCORES[self.__sqft()][0]
            score -= self.ROOMSCORES[self.__size()][0]
            score -= self.LAUNDRYSCORES[self.__laundry()][0]
            currentDT = datetime.datetime.now()
            DTString = currentDT.strftime("%Y-%m-%d %H:%M:%S")
            try:
                imageinfo = self.html.find('meta', attrs={'property': 'og:image'})['content']
            except TypeError:
                imageinfo = 'none'

            data_return = {
                'Time':  DTString,
                'Score': score,
                'Internet': self.INTERNETSCORES[self.__internet()][1],
                'Price': self.PRICESCORES[self.__price()][1],
                'Laundry': self.LAUNDRYSCORES[self.__laundry()][1],
                'Sqft': self.SIZESCORES[self.__sqft()][1],
                'Rooms': self.ROOMSCORES[self.__size()][1],
                'imagelink': imageinfo
            }
            return data_return

    def __price(self):
        self.price = self.html.find('span', attrs={'class': 'price'}).string
        self.price = int(self.price.strip(',$'))

        if self.price < 800:
            return 'A'
        elif self.price < 900:
            return 'B'
        elif self.price < 1100:
            return 'C'
        else:
            return 'D'

    def __internet(self):
        # Regex for "google fiber"
        if not re.search('google[\s-]?fiber', str(self.body), re.IGNORECASE):
            if not re.search('high[\s-]?speed[\s-]?internet', str(self.body), re.IGNORECASE):
                return "C"
            else:
                return "B"
        else:
            return "A"

    def __size(self):
        try:
            rooms = re.search('(\dbr)|(studio)', str(self.sizeinfo), re.IGNORECASE).group(0)
            print(rooms)
        except AttributeError:
            print('No rooms found')
            return 'D'

        if re.match('2br', rooms, re.IGNORECASE):
            return 'A'
        elif re.match('1br', rooms, re.IGNORECASE):
            return 'B'
        elif re.match('studio', rooms, re.ignorecase):
            return 'C'
        else:
            return 'D'

    def __sqft(self):
        self.sqft = re.search('\d{3,4}ft', str(self.sizeinfo), re.IGNORECASE)
        try:
            self.sqft = int(self.sqft.group(0).strip('ft'))
            print(self.sqft)
        except AttributeError:
            print("No sqft found")
            return 'F'

        if self.sqft < 300:
            return 'A'
        elif self.sqft < 450:
            return 'B'
        elif self.sqft < 600:
            return 'C'
        elif self.sqft < 750:
            return 'D'
        elif self.sqft < 900:
            return 'E'
        else:
            return 'F'

    def __laundry(self):
        if re.match('w/d in unit', self.html.text, re.IGNORECASE):
            return 'A'
        else:
            return 'B'

    def __autoreject(self):
        for rejectstring in self.AUTOREJECT:
            if re.match(rejectstring, str(self.body), re.IGNORECASE):
                return True
            else:
                return False
