import requests
from bs4 import BeautifulSoup
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import time
import random


def run():
    # لیستی از User-Agentهای مختلف
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
    ]

    # انتخاب User-Agent تصادفی
    random_user_agent = random.choice(user_agents)
    import time
    # اضافه کردن پارامتر زمانی به URL
    url = f'https://www.tgju.org/gold-chart?ts={int(time.time())}'

    # تنظیم هدرهای HTTP شامل User-Agent تصادفی
    headers = {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Expires': '0',
        'User-Agent': random_user_agent
    }

    # ارسال درخواست با هدرها و پارامتر زمان
    response = requests.get(url, headers=headers)

    # بررسی اینکه درخواست موفقیت‌آمیز بوده
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # متغیرهایی برای ذخیره داده‌ها
        rows = []

        # پیدا کردن تمام ردیف‌های جدول
        table_rows = soup.find_all('tr', {'data-market-row': True})  # انتخاب تمام ردیف‌هایی که اطلاعات قیمت دارند
        for row in table_rows:
            gold_type = row.find('th').text.strip()  # استخراج نوع طلا از تگ th
            cols = row.find_all('td')  # استخراج قیمت‌ها و سایر داده‌ها از تگ‌های td

            live_price = cols[0].text.strip()  # قیمت زنده
            change = cols[1].find('span').text.strip()  # تغییرات قیمت از داخل تگ span
            min_price = cols[2].text.strip()  # کمترین قیمت
            max_price = cols[3].text.strip()  # بیشترین قیمت
            time = cols[4].text.strip()  # زمان

            # اضافه کردن داده‌ها به لیست
            rows.append([gold_type, live_price, change, min_price, max_price, time])

        # تنظیم دسترسی به Google Sheets API
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file('gold-price-438507-fc1018d6828f.json', scopes=scope)
        client = gspread.authorize(creds)

        # باز کردن Google Sheet
        sheet = client.open_by_key('1Q-k-UTdl-yfxT1if2EanEOhKdgLRsK2_VcJm1uKOC3w').worksheet('tgju')

        # پاک کردن شیت قبلی
        sheet.clear()

        # اضافه کردن نام ستون‌ها در ردیف اول
        headers = ['قیمت طلا', 'قیمت زنده', 'تغییر', 'کمترین قیمت', 'بیشترین قیمت', 'زمان']
        sheet.append_row(headers)

        # اضافه کردن داده‌های DataFrame به Google Sheets
        sheet.append_rows(rows)

        print("داده‌ها با موفقیت در Google Sheets آپلود شدند.")
    else:
        print(f"خطا در دسترسی به سایت: {response.status_code}")


if __name__ == '__main__':
    while True:
        run()
        print('run okay')
        time.sleep(30 * 60)