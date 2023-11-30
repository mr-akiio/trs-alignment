# Traces Alignment

This project is trying to align traces by using peak-based alignment and correlation-based alignment.

To run this project you need to install trsfile, matplotlib and numpy. You can use `pip` to download it.

Each python file will create new file with changed traces, with appropiate naming (usualy as +file_name). On the beggining of each python file, there are some global variables you can change. To see the traces use `visualize.py`.

Run in terminal as:
> **python file.py traces.trs**

You can find here already two files with misalign traces. One contains 5 traces and other 10. You can run them trough `peak_alignment.py` or `cross-correlation.py` to see the results.

There is one more file with 10 traces. These are not misalign and you can do with them what you want.
You can use two more python files to work with traces.
- `misalign.py` will misalign traces it gets as parameter.
- `saveAs.py` will save number of traces you will set in global variables
