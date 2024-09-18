from scrapy.selector import Selector

def parse_desc_list(dl: Selector) -> dict:
    """Parse a <dl> subtree into dict.

    Ignores children not belonging to the <dl> format.
    """

    keys = []
    values = []

    kseg_n = 0

    for elem in dl.xpath('*'):
        name = elem.xpath('name()').get()
        text = elem.xpath('string()').get().strip()
        if name == 'dt':
            keys.append(text)
            kseg_n += 1
            ex_kseg = True  # Flag: "[would be] exiting a key segment?"
        elif name == 'dd':
            if ex_kseg:
                vseg = []
                for i in range(0, kseg_n):  # Map a copy of the value
                    values.append(vseg)     # segment for each new key.
                kseg_n = 0
                ex_kseg = False
            vseg.append(text)  # Distribute value among each new key.

    return dict(zip(keys, values))
