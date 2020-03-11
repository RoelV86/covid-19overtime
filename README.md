# covid-19overtime
> This code generates animated gifs of COVID-19 data. The data is obtained from the [JHU repository](https://github.com/CSSEGISandData/COVID-19).

## Output
![COVID-19: Confirmed cases](/confirmed.gif)
![COVID-19: Deaths](/deaths.gif)
![COVID-19: Sick](/sick.gif)

## Usage
Run it. It will generate images for every day, skipping the days where there is already data in the df_history.csv file. Delete (parts of) the file to rerun it. 

The data repository country names sometimes do not match the names in the geometry file. There is a section in the code where the countries are renamed.

## Sources
* Data about COVID-19 cases from [JHU repository](https://github.com/CSSEGISandData/COVID-19)
* Geometry data from [Natural Earth Data](https://www.naturalearthdata.com/downloads/110m-cultural-vectors/)

