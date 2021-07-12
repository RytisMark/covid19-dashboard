# COVID-19 dashboard

***! Keep in mind that this project still got some issues that need fixing, but the majority of the work (I think), is done.***

A project in which I decided to code a COVID-19 dashboard.

The dashboard displays tabs with total cases, total deaths, total recoveries and total active cases. It also shows a table with all the countries and its aforementioned numbers; a circle map with the same data shown when hovered over; and three different charts - one showing the linear or logarithmic increase of cases of any country; second showing daily increase in cases; and the third showing first 15 countries according to the magnitude of COVID-19 cases.

You can see how it looks by running the code, or by looking at these screenshots:

![image-1](https://user-images.githubusercontent.com/39343969/125302868-0618ea00-e335-11eb-8541-d4cae6ad0016.png)
![image-2](https://user-images.githubusercontent.com/39343969/125302885-0a450780-e335-11eb-9b27-da779b68f991.png)

The first time I wrote this project, I did it in a Jupyter Notebook (.ipynb), but I have also rewrote it in plain Python (.py) for anyone that do not use Jupyter.

If you are using the Jupyter version, you will need to install these packages:
```
pip install plotly
pip install pandas
pip install numpy
pip install jupyter-dash
pip install folium
pip install dash-bootstrap-components
```

If you are using the Python version, install the same packages, except use
```
pip install dash
```
instead of
```
pip install jupyter-dash
```
.