from bs4 import BeautifulSoup
import json
import datetime
import os
import sys
import requests

URL = "https://portal.nau.edu.ua/schedule/group?id=361" # Обери свою групу в на сайті КАІ - https://portal.nau.edu.ua/schedule/group/list

subgroup = 2    # 2 або 1
parity = 1      # 2 або 1

UKRAINIAN_DAYS = {
    "monday": "понеділок",
    "tuesday": "вівторок",
    "wednesday": "середа",
    "thursday": "четвер",
    "friday": "п'ятниця",
    "saturday": "субота",
    "sunday": "неділя"
}

OLD_FILE = "rozklad_old.html"
NEW_FILE = "rozklad_new.html"

def fetch_schedule():
    try:
        response = requests.get(URL, timeout=5)
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        print("\033[91mСайт КАІ приліг :((. Інформацію беру із локального старого розкалду...\033[0m")
        if os.path.exists(OLD_FILE):
            with open(OLD_FILE, "r", encoding="utf-8") as f:
                return f.read()
        else:
            print("\033[91mСтарий розклад теж не знайдено.\033[0m")
            sys.exit(1)
    

def save_schedule(html, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

def compare_schedules():
    if os.path.exists(NEW_FILE):
        if os.path.exists(OLD_FILE):
            with open(OLD_FILE, "r", encoding="utf-8") as f1, open(NEW_FILE, "r", encoding="utf-8") as f2:
                if f1.read() != f2.read():
                    print("\033[91mРозклад змінився.\033[0m")
                    print(f"Старий: file://{os.path.abspath(OLD_FILE)}")
                    print(f"Новий: {URL}")
        os.replace(NEW_FILE, OLD_FILE)

def parse_schedule(html):
    soup = BeautifulSoup(html, 'html.parser')
    schedule_data = {}
    weeks = soup.find_all('div', class_='wrapper')
    
    for week in weeks:
        week_title = week.find('h2').text.strip()
        week_number = int(week_title.split()[-1])
        schedule_data[week_number] = {}
        
        days = [th.text.strip().lower() for th in week.find_all('th', class_='day-name')]
        rows = week.find_all('tr')[1:]
        
        for row in rows:
            hour_cell = row.find('th', class_='hour-name')
            if not hour_cell:
                continue
            time_slot = hour_cell.find('div', class_='full-name').text.strip()
            
            for i, cell in enumerate(row.find_all('td')):
                if i >= len(days):
                    continue
                day = days[i]
                schedule_data[week_number].setdefault(day, [])
                
                pairs = cell.find_all('div', class_='pair')
                for pair in pairs:
                    subject = pair.find('div', class_='subject')
                    if not subject:
                        continue
                    subject = subject.text.strip()
                    subgroup_tag = pair.find('div', class_='subgroup')
                    subgroup = subgroup_tag.text.strip().split()[-1] if subgroup_tag else "Обидві"
                    teacher = pair.find('div', class_='teacher')
                    teacher = teacher.text.strip() if teacher else "Невідомий викладач"
                    room = pair.find('div', class_='room')
                    room = room.text.strip() if room else "Без аудиторії"
                    
                    schedule_data[week_number][day].append({
                        'time': time_slot,
                        'subject': subject,
                        'subgroup': subgroup
                    })
    return schedule_data

def get_schedule(schedule, week, day, subgroup):
    day = day.lower()
    if week not in schedule or day not in schedule[week]:
        return "Розкладу немає"
    
    day_schedule = [item for item in schedule[week][day] if item['subgroup'] in [subgroup, "Обидві"]]
    return day_schedule if day_schedule else "Занять немає"

oppositparity = 2 if parity == 1 else 1

if __name__ == "__main__":
    html = fetch_schedule()
    save_schedule(html, NEW_FILE)
    compare_schedules()
    
    schedule = parse_schedule(html)
    
    today = datetime.datetime.today()
    week_num = parity if (today.isocalendar()[1] % 2 == 0) else oppositparity
    day_name = UKRAINIAN_DAYS[today.strftime('%A').lower()]
    subgroup = str(subgroup)
    
    if len(sys.argv) > 1:
        try:
            offset = int(sys.argv[1])
            target_date = today + datetime.timedelta(days=offset)
            day_name = UKRAINIAN_DAYS[target_date.strftime('%A').lower()]
            
            # Обчислення днів до кінця поточного тижня, включаючи сьогодні
            days_to_end_of_week = 6 - today.weekday()
            
            # Якщо зміщення відбувається в межах цього тижня
            if offset <= days_to_end_of_week:
                week_num = parity if (today.isocalendar()[1] % 2 == 0) else oppositparity
            else:
                # Обчислення залишкових днів після закінчення цього тижня
                remaining_days = offset - days_to_end_of_week - 1
                week_diff = (remaining_days // 7) + 1  # +1 для переходу на наступний тиждень
                
                # Зміна парності тижня, якщо перехід на непарну кількість тижнів
                if week_diff % 2 != 0:
                    week_num = oppositparity if week_num == parity else parity
                    
        except ValueError:
            print("Невірний формат дня. Використовуйте ціле число для зсуву.")
            sys.exit(1)
    
    print(f"\t\t{day_name} //: {week_num}")
    
    result = get_schedule(schedule, week_num, day_name, subgroup)
    print(json.dumps(result, indent=2, ensure_ascii=False))

