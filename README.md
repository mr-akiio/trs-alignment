# Traces Alignment

This project is trying to align traces by using peak-based, correlation-based and extremes-based alignment.

To run this project you need to install trsfile, matplotlib, scipy and numpy. You can use `pip` to download it.
To get this done You can execute this command from trs-alignment directory:
> **pip install -r requirements.txt**

Each python file will create new file with changed traces, with appropiate naming with what allignment method was used (usualy as +METHOD(parameters)). 
On the beggining of each python file, there are some global variables you can change. To see the traces use `visualize.py`.

Run in terminal as:
> **python file.py traces.trs**

You can find here already two files with misalign traces. One contains 5 traces and other 10. 
You can run them trough `peak_alignment.py`, `cross-correlation.py` or `extremes_alignment.py` to see the results. 
In case of using `extremes_alignment.py` be aware of that it uses `utils.py` where are another constants to play with.

There is one more file with 10 traces. These are not misaligned and you can do with them what you want.
You can use two more python files to work with traces.
- `misalign.py` will misalign traces it gets as parameter.
- `saveAs.py` will save number of traces you will set in global variables
