# kaiWeek
консольний прикол для моніторингу змін розкладу та його відображення

Див. 'kaiWeek.py' для налаштування групи та підгрупи. 

# Instalation:


## Linux:

`git clone https://github.com/ebede2g/kaiWeek.git`

`cd kaiWeek`

`python3 -m venv venv`

`source venv/bin/activate && pip install -r requirements.txt`


Запуск 

`python3 kaiWeek.py`


## Windows:
Переконайсь шо маєш гіт. Якщо не маєш гіт'а, то варто втсановити

`git --version`

`winget install --id Git.Git -e --source winget`

Після чого закрий та наново відкрий cmd

`git clone https://github.com/ebede2g/kaiWeek.git`

`cd kaiWeek`

`py -m pip install -r requirements.txt`


Запуск 

`py kaiWeek.py`





![Alt text](./Screenshot_20250218_210921.png)

По додатковому функціоналу: приймаються цілочисельні агрументи після скрипту, які дозволяють перглядати розклад на інші дні за принципом "додати к-сть днів до сьогодні":

`python3 kaiWeek.py 1` - відобразить розклад на завтра

`python3 kaiWeek.py -2` - відобразить розклад на післявчора


(скрипт не протестований і взагалі я їбав той шитпост гпт тестити ше, шліть pull request)
