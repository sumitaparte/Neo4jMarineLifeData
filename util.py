from bs4 import BeautifulSoup
import requests


def get_soup(url) -> BeautifulSoup:
    response = requests.get(url)
    html = response.content
    soup = BeautifulSoup(html.decode("utf-8"), features="html.parser")
    return soup

