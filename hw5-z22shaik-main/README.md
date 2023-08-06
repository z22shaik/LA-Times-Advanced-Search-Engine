# hw5-z22shaik
Instructions for Running Code: </br>
 </br> To run BM25 retrieval use bm25.py:
  - To run bm25.py: (Type the following into your terminal) python3.9 bm25.py (file folder location for inverted index) (file path to queries) (output file path for rankings txt file)
  
  To gather metrics for baseline results vs. monoBERT results, use example.py.
  - To run example.py: (Type the following into your terminal) python3.9 --qrel (INSERT QREL FILE LOCATION) --results (INSERT FILE LOCATION FOR RESULTS FILE)
  - Essentially, for a given results file, the program will output a CSV file with the five measures used for analysis
  
  To perform a p-test and gauge improvement given baseline results and a candidate, use stat_sig.py:	
  - (Type the following into your terminal) Python3.9 stat_sig.py
  - Array’s for each measure should be updated using CSV values that are outputted in example.py to perform p-tests
  
  To run HW5 Notebook.ipynb:
  - Press the “play” button for each code block

