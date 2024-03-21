from langchain_community.document_loaders import BSHTMLLoader
from langchain_core.documents import Document

import functools
import pandas
import pickle
import typing
import tqdm
import bs4
import os


# UTF-8 encoding has been messed up by the original parsing
REPL: typing.Final[dict[str, str]] = {
    '\xa0': ' ',
    '&auml;': 'ä',
    '&ouml;': 'ö',
    '&uuml;': 'ü',
    '&Auml;': 'Ä',
    '&Ouml;': 'Ö',
    '&Uuml;': 'Ü',
    '&szlig;': 'ß'
}


def set_nested_value(dict_obj, keys, value):
    for key in keys[:-1]:
        dict_obj = dict_obj.setdefault(key, {})

    dict_obj[keys[-1]] = value


class DatapointBSHTMLLoader(BSHTMLLoader):
    def __init__(self, html, path, title, url):
        super().__init__(None)
        self.html = html
        self.path = path
        self.title = title
        self.url = url

    def lazy_load(self):
        text = self.html.get_text(self.get_text_separator).split('\n')
        text = '\n'.join(filter(lambda x: x.strip() != '', text))

        metadata = {
            "source": self.path,
            "title": self.title,
            "url": self.url,
        }
        yield Document(page_content=text, metadata=metadata)


class TqdmFileWrapper:
    def __init__(self, file, progress_bar):
        self._file = file
        self._progress_bar = progress_bar

    def read(self, size=-1):
        _data = self._file.read(size)
        self._progress_bar.update(len(_data))
        return _data

    def readline(self, size=-1):
        line = self._file.readline(size)
        self._progress_bar.update(len(line))
        return line

    # Add any other methods from the file object you might need
    def close(self):
        self._file.close()


class Data:
    XLSX_PATH: typing.Final[str] = 'data/st-gallen-data-new.xlsx'
    PICKLE_PATH: typing.Final[str] = 'data/data.pickle'

    def __init__(self, path):
        self.raw_data = pandas.read_excel(path, sheet_name=None)
        self.info_key, self.data_key = self.raw_data.keys()
        self.page_count = self.raw_data[self.info_key].iloc[0, 0]
        self.voice_count = self.raw_data[self.info_key].iloc[0, 1]

        # LoL, clean your        v    dataset bois
        assert self.page_count + 1 == len(self.raw_data[self.data_key])

        self.data = {}

    @staticmethod
    def _soup_to_vitals(soup) -> tuple[str, bs4.BeautifulSoup]:
        if soup.title is not None:
            title = soup.title.string
            title = title.split(' | ')[0]

        else:
            title = ''

        decompositions = ['head', 'header', 'style', 'nav', 'script']
        for tag_name in decompositions:
            if getattr(soup, tag_name) is None:
                continue

            for tag in soup.find_all(tag_name):
                tag.decompose()

        desktop_menu_column = soup.find('div', class_='desktop-menu-column')
        if desktop_menu_column is not None:
            desktop_menu_column.decompose()

        rsimg = soup.find('span', class_='rsimg')
        if rsimg is not None:
            rsimg.decompose()

        headerprint = soup.find('div', id='headerprint')
        if headerprint is not None:
            headerprint.decompose()

        accesskeys = soup.find('div', id='accesskeys')
        if accesskeys is not None:
            accesskeys.decompose()

        cpr = soup.find('span', class_='copyright')
        if cpr is not None:
            cpr.decompose()

        footer = soup.find('section', class_='footer')
        if footer is not None:
            footer.decompose()

        for tag in soup.find_all(True):
            if tag.string is None or tag.name == 'li':
                continue

            tag.string = functools.reduce(
                lambda s, kv: s.replace(*kv), REPL.items(), tag.string)

        binary = soup.encode('latin1', errors='replace')
        text = binary.decode('utf-8', errors='replace')
        return title, bs4.BeautifulSoup(text, 'html.parser')

    def load_from_raw(self):
        rows = self.raw_data[self.data_key].iterrows()
        for i, row in tqdm.tqdm(rows, total=self.page_count):
            filepath = f'{row["path_to_data_files"]}/data'
            with open(f'{filepath}.html', 'r') as html_file:
                html = bs4.BeautifulSoup(html_file, 'html.parser')
                title, soup = self._soup_to_vitals(html)
                datapoint = DatapointBSHTMLLoader(
                    soup, filepath, title, row['source'])
                set_nested_value(self.data, filepath.split('/'), datapoint)

    def load_from_pickle(self, file_path=PICKLE_PATH):
        file_size = os.path.getsize(file_path)
        with (open(file_path, 'rb') as f,
              tqdm.tqdm(total=file_size, unit_scale=True) as pbar):

            wrapped_file = TqdmFileWrapper(f, pbar)
            self.data = pickle.load(wrapped_file)

    def export_data(self):
        with open(Data.PICKLE_PATH, 'wb') as f:
            pickle.dump(self.data, f)

    def yield_datapoints(self, data=None):
        if data is None:
            data = self.data

        for key, value in data.items():
            if isinstance(value, DatapointBSHTMLLoader):
                yield value

            else:
                yield from self.yield_datapoints(value)