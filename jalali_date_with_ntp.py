# jalali_date_with_ntp.py
# یک ماژول MicroPython برای دریافت زمان از NTP و تبدیل به تاریخ جلالی (فارسی) با تنظیم منطقه زمانی صحیح

import ntptime
import network
import utime

# تنظیمات Wi-Fi
SSID = ""  # SSID واقعی را جایگزین کنید
PASSWORD = ""  # رمز عبور واقعی را جایگزین کنید

def connect_wifi():
    """
    اتصال به شبکه Wi-Fi.
    بازگشت:
        bool: True اگر متصل شد، False در غیر این صورت
    """
    try:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if not wlan.isconnected():
            wlan.connect(SSID, PASSWORD)
            for _ in range(10):  # تا 10 ثانیه صبر کنید
                if wlan.isconnected():
                    return True
                utime.sleep(1)
        else:
            return True
        return False
    except Exception:
        return False

def set_ntp_time(server="ir.pool.ntp.org"):
    """
    تنظیم زمان سیستم از سرور NTP.
    آرگومان‌ها:
        server (str): آدرس سرور NTP (پیش‌فرض: ir.pool.ntp.org)
    بازگشت:
        bool: True اگر موفق بود، False در غیر این صورت
    """
    try:
        ntptime.host = server
        ntptime.settime()
        return True
    except Exception:
        return False

# توابع تبدیل اصلاح‌شده از jalaali-python
def g2d(gy, gm, gd):
    """
    تبدیل تاریخ میلادی به شماره روز جولیان.
    آرگومان‌ها:
        gy (int): سال میلادی
        gm (int): ماه میلادی
        gd (int): روز میلادی
    بازگشت:
        int: شماره روز جولیان
    """
    a = (14 - gm) // 12
    y = gy + 4800 - a
    m = gm + 12 * a - 3
    jd = gd + ((153 * m + 2) // 5) + 365 * y + (y // 4) - (y // 100) + (y // 400) - 32045
    return jd

def d2g(jdn):
    """
    تبدیل شماره روز جولیان به تاریخ میلادی.
    آرگومان‌ها:
        jdn (int): شماره روز جولیان
    بازگشت:
        tuple: (سال، ماه، روز) میلادی
    """
    l = jdn + 68569
    n = (4 * l) // 146097
    l = l - (146097 * n + 3) // 4
    i = (4000 * (l + 1)) // 1461001
    l = l - (1461 * i) // 4 + 31
    j = (80 * l) // 2447
    d = l - (2447 * j) // 80
    l = j // 11
    m = j + 2 - (12 * l)
    y = 100 * (n - 49) + i + l
    return y, m, d

def jal_cal(jy):
    """
    محاسبه جزئیات تقویم جلالی برای یک سال معین.
    آرگومان‌ها:
        jy (int): سال جلالی
    بازگشت:
        dict: اطلاعات سال شامل کبیسه، سال میلادی و روز شروع
    """
    breaks = [-61, 9, 38, 199, 426, 686, 756, 818, 1111, 1181, 1210, 1635, 2060, 2097, 2192, 2262, 2324, 2394, 2456, 3178]
    bl = len(breaks)
    gy = jy + 621
    leapj = -14
    jp = breaks[0]
    if jy < jp or jy >= breaks[bl - 1]:
        raise ValueError('سال جلالی نامعتبر %s' % jy)
    jump = 0
    for i in range(1, bl):
        jm = breaks[i]
        jump = jm - jp
        if jy < jm:
            break
        leapj = leapj + (jump // 33 * 8) + ((jump % 33) // 4)
        jp = jm
    n = jy - jp
    leapj = leapj + (n // 33 * 8) + (((n % 33) + 3) // 4)
    if (jump % 33) == 4 and jump - n == 4:
        leapj += 1
    leapy = (gy // 4) - ((gy // 100) + 1) * 3 // 4 - 150
    march = 20 + leapj - leapy
    if jump - n < 6:
        n = n - jump + ((jump + 4) // 33 * 33)
        leap = (((n + 1) % 33 - 1) % 4)
        if leap == -1:
            leap = 4
    else:
        leap = ((n % 33) + 3) % 4
        if leap == 4:
            leap = 0
    return {'leap': leap, 'gy': gy, 'march': march}

def d2j(jdn):
    """
    تبدیل شماره روز جولیان به تاریخ جلالی.
    آرگومان‌ها:
        jdn (int): شماره روز جولیان
    بازگشت:
        dict: دیکشنری حاوی سال، ماه و روز جلالی
    """
    gy = d2g(jdn)[0]
    jy = gy - 621
    jcal = jal_cal(jy)
    jdn1f = g2d(gy, 3, jcal['march'])
    k = jdn - jdn1f
    if k >= 0:
        if k <= 185:
            jm = 1 + (k // 31)
            jd = (k % 31) + 1
            return {'jy': jy, 'jm': jm, 'jd': jd}
        else:
            k -= 186
    else:
        jy -= 1
        k += 179
        if jcal['leap'] == 1:
            k += 1
    jm = 7 + (k // 30)
    jd = (k % 30) + 1
    return {'jy': jy, 'jm': jm, 'jd': jd}

def gregorian_to_jalali(gy, gm, gd):
    """
    تبدیل تاریخ میلادی به تاریخ جلالی.
    آرگومان‌ها:
        gy (int): سال میلادی (مثلاً 2025)
        gm (int): ماه میلادی (1-12)
        gd (int): روز میلادی (1-31)
    بازگشت:
        tuple: (سال جلالی، ماه جلالی، روز جلالی) یا None اگر نامعتبر باشد
    """
    try:
        jdn = g2d(gy, gm, gd)
        jalali = d2j(jdn)
        return jalali['jy'], jalali['jm'], jalali['jd']
    except Exception:
        return None

def get_jalali_datetime():
    """
    دریافت تاریخ و زمان فعلی در تقویم جلالی از NTP با تنظیم منطقه زمانی IRST.
    بازگشت:
        dict: دیکشنری حاوی سال، ماه، روز، ساعت، دقیقه، ثانیه جلالی یا None در صورت شکست
    """
    try:
        if not connect_wifi():
            return None
        if not set_ntp_time():
            return None
        # دریافت زمان UTC
        t = utime.localtime()
        # تبدیل به ثانیه از مبدأ
        seconds = utime.mktime(t)
        # افزودن افست برای IRST: UTC+3:30 = 12600 ثانیه
        local_seconds = seconds + 12600
        # دریافت تاپل زمان محلی
        local_t = utime.localtime(local_seconds)
        year, month, day = local_t[0], local_t[1], local_t[2]
        hour, minute, second = local_t[3], local_t[4], local_t[5]
        # تبدیل به جلالی
        jalali_date = gregorian_to_jalali(year, month, day)
        if jalali_date is None:
            return None
        j_year, j_month, j_day = jalali_date
        return {
            'year': j_year,
            'month': j_month,
            'day': j_day,
            'hour': hour,
            'minute': minute,
            'second': second
        }
    except Exception:
        return None

def format_jalali_datetime(dt):
    """
    فرمت کردن تاریخ و زمان جلالی به صورت رشته با ماه عددی.
    آرگومان‌ها:
        dt (dict): دیکشنری از get_jalali_datetime
    بازگشت:
        str: رشته فرمت‌شده (مثلاً '1404/02/30 23:15:45') یا پیام خطا
    """
    if dt is None:
        return "خطا: تاریخ یا زمان نامعتبر"
    return "{:04d}/{:02d}/{:02d} {:02d}:{:02d}:{:02d}".format(
        dt['year'], dt['month'], dt['day'],
        dt['hour'], dt['minute'], dt['second']
    )

# مثال استفاده
if __name__ == "__main__":
    jalali_dt = get_jalali_datetime()
    print(format_jalali_datetime(jalali_dt))