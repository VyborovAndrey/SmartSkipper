<p style="display:inline-block">
  <a href="https://www.python.org/downloads/release/python-3110/">
    <img src="https://img.shields.io/badge/Python-3.11-blue">
  </a>
  <a href="https://github.com/kivy/kivy">
    <img src="https://img.shields.io/badge/Kivy-2.2.1-green">
  </a>
  <a href="https://pypi.org/project/geovectorslib/">
    <img src="https://img.shields.io/badge/geovectorslib-1.4-green">
  </a>
  <a href="https://github.com/numpy/numpy">
    <img src="https://img.shields.io/badge/numpy-1.26.2-green">
  </a>
  <a href="https://github.com/scipy/scipy">
    <img src="https://img.shields.io/badge/SciPy-1.11.4-green">
  </a>
  <a href="https://github.com/opencv/opencv-python">
    <img src="https://img.shields.io/badge/opencv--python-4.8.1.78-green">
  </a>
  <a href="https://github.com/nidhaloff/gpx-converter">
    <img src="https://img.shields.io/badge/gpx--converter-2.1.0-green">
  </a>
  <a href="https://github.com/ecmwf/eccodes">
    <img src="https://img.shields.io/badge/eccodes-1.6.1-green">
  </a>
  <a href="https://pypi.org/project/cfgrib/">
    <img src="https://img.shields.io/badge/cfgrib-0.9.10.4-green">
  </a>
</p>

# SmartSkipper
В папке project находится проект “Генерация GPX файлов парусных гонок и алгоритм поиска самого быстрого маршрута парусного судна”

- Генерация файлов происходит в соответствии с правилами парусных гонок.\
  Ставится два стартовых знака перпендикулярно ветру, а также ставится верхний знак против ветра на некотором расстоянии. После этого лодки идут в лавировку от стартовых до верхнего знака, а затем спускаются до стартового знака и финишируют. При движении вниз по ветру лодка может идти курсом фордевинд (строго вниз по ветру) или курсом бакштаг (под некоторым углом к ветру).\
  После чего парусная гонка сохраняется в формате GPX.\
- Алгоритм поиска самого быстрого маршрута основан на методе изохрон, то есть формируется изохрона –  линия, показывающая точки с одинаковым временем достижения из заданного места. Скорость движения     парусного судна – функция от ветра и характеристик лодки.\
  Для получения информации о ветре используются прогнозы [Global Forecast System](https://www.ncei.noaa.gov/products/weather-climate-models/global-forecast),  представляющие из себя GRIB файлы.\
  Для получения информации о характеристиках парусного судна используются полярные графики скоростей в формате CSV. Пример работы алгоритма для поиска кратчайшего пути на скриншотах ниже.

  <p align="center">
    <img src="media/optimal1.png"> 
    <p align="center"> Рисунок 1 - Построенный оптимальный маршрут <p>
  </p>
  <p align="center">
    <img src="media/optimal2.png">
    <p align="center"> Рисунок 2 - Изохроны, использующиеся для вычисления оптимального маршрута <p>
  </p>


В папке coursework находится приложение Smartskipper.

- Smartskipper - приложение для анализа ваших тренировок и гонок в мире парусного спорта. Загружайте ваши треки и узнайте, где вы бы могли стать быстрее. Приложение позволяет вывести на ваш экран такие характеристики как: Course (курс движения), Angle to the wind (угол движения к ветру), Course Over Ground (скорость движения), Velocity Made Good (скорость продвижения вверх по ветру). Пример на скриншоте ниже.
 
  <p align="center">
    <img src="media/race.png">
    <p align="center"> Рисунок 3 - Сгенерированная гонка и отображение параметров <p>
  </p>

Для запуска проекта потребуются библиотеки, которые можно установить при помощи команд:
```
pip install kivy
pip install kivymd
pip install kivy-Garden
pip install kivy-garden.mapview
pip install geovectorslib
pip install numpy
pip install SciPy
pip install opencv-python
pip install gpx-converter
pip install eccodes
pip install cfgrib
```
