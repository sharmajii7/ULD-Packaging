# ULD Packing

The repository implements 3-D bin packing into multiple bins keeping constraints of weight-limit and other important constraints of stability,etc.

## How to Run:

### Install the reuired python packages

```bash
$ pip install matplotlib streamlit numpy
```

#### Use the main.py to run the code

In the main function change the file path of the input file and simply run

```bash
$ python main.py
```
This gives the output on the output file with every package id having the uld_id it has been assigned and the coordinated of its begining and the opposite corner in a comma seperated format

Visualizations for each ULD are also generated by using the matplotlib library
![WhatsApp Image 2024-12-04 at 13 00 14_9bebf92e](/Packing_Preview.jpg)


#### Use the GUI Interface

Run the file deploy.py to run a streamlit application hosted on http://localhost:8501/

In this you can select your input text file and directly run the assignment from Run Assignment button

```
$ streamlit run deploy.py
```
In order to get interactive visualization of the packages use:
```
$ streamlit run deployOld.py
```
After the assignment is run the output file and the file containing the ids of the packages not assigned to any uld can be downloaded.
Also the space optimization and visualisation is also presented when the assignment function is run
![image](/Streamlit_SS.png)

### Validation of the output
The output can be validated on all constraint grounds by running the Validaton.py file change the file path of the output file accordingly.
```bash
$ python Validation.py
```
