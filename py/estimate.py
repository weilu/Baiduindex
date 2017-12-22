import time
from datetime import date, datetime
from dateutil import rrule
from PIL import Image
from Baiduindex import (openbrowser, visit_baidu_trends, set_date_range,
                        restore_city_selector, find_city, extract_score,
                        get_data_read)

def getindex(keyword, browser):
    visit_baidu_trends(keyword)
    outfile = "../baidu/trends.csv"
    data_read = get_data_read(outfile)

    with open(outfile, "a+") as output:
        if not data_read:
            output.write('city,date,score\n')
        with open("../config/prefectures.txt", "r") as input_cities:
            cities = input_cities.read().splitlines()
            for city in cities:
                if city in data_read:
                    print(f'{city} already processed, skipping')
                    continue
                try:
                    if find_city(city):
                        set_date_range('all')
                        save_page_source(browser, city)
                        min, max = parse_y_axis(browser, city)
                        scores = estimate_scores(browser, min, max)
                        for date, score in scores:
                            output.write(f'{city},{date},{score}\n')
                    else:
                        print(f'{city} not found')
                    restore_city_selector()
                    time.sleep(1.12)
                except Exception as err:
                    print(f'Error while parsing scores for city {city}')
                    print(err)
                    visit_baidu_trends(keyword)


def save_page_source(browser, city):
    html = browser.page_source
    with open(f"../raw_estimate/{city}.html", "w") as output:
        output.write(html)


def estimate_scores(browser, min, max):
    start = date(2011, 1, 2)
    until = date(2017, 12, 23)
    weeks = rrule.rrule(rrule.WEEKLY, dtstart=start, until=until)
    # starts from 2011-01-01 (Saturday), week starts every sunday
    weeks = [datetime(2011, 1, 1)] + list(weeks)
    total = len(weeks)
    print(f'weeks: {total}')
    browser.execute_script(open("../js/parse.js", ).read(), total, min, max)
    data = browser.get_log('browser')
    scores = data[-1]['message'].split(' ')[-1].replace('"', '').split(',')
    scores = [float(x) for x in scores]
    assert len(scores)==total
    return list(zip(weeks, scores))


def parse_y_axis(browser, city):
    imgelement = browser.find_element_by_xpath('//*[@id="trendYimg"]')
    locations = imgelement.location

    # offset by scroll amount
    scroll = browser.execute_script("return window.scrollY;")
    top = locations['y'] - scroll
    sizes = imgelement.size

    # 截取当前浏览器
    path = "../raw_estimate/original_" + city
    browser.save_screenshot(str(path) + ".png")

    browser.execute_script("document.getElementById('trend').style.visibility='hidden'");

    path = "../raw_estimate/" + city
    browser.save_screenshot(str(path) + ".png")

    # 打开截图切割
    img = Image.open(str(path) + ".png")
    num_markers = 7
    x_top = int(locations['x'] + sizes['width'] / 2)
    x_bottom = int(locations['x'] + sizes['width'])
    max_crop_top_left_bottom_right = (x_top, int(top),
            x_bottom, int(top + sizes['height']/num_markers))
    jpg = img.crop(max_crop_top_left_bottom_right)
    (w, h) = jpg.size
    jpg = jpg.resize((2*w, 2*h), Image.ANTIALIAS)
    jpg.save(str(path) + "_y_max.jpg")
    max = extract_score(jpg)
    if not max:
        max = int(input("Failed to parse max y, please input："))
    print(f'max: {max}')

    y_top = int(top) + sizes['height']/num_markers * (num_markers - 1)
    min_crop_top_left_bottom_right = (x_top, y_top,
            x_bottom, int(top + sizes['height']))
    jpg = img.crop(min_crop_top_left_bottom_right)
    jpg = jpg.resize((2*w, 2*h), Image.ANTIALIAS)
    jpg.save(str(path) + "_y_min.jpg")
    min = extract_score(jpg)
    if not min:
        min = int(input("Failed to parse min y, please input："))
    print(f'min: {min}')

    browser.execute_script("document.getElementById('trend').style.visibility='visible'");

    return (min, max)


if __name__ == "__main__":
    browser = openbrowser()
    getindex("维稳", browser)
