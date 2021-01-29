ocr_processing for Harley Spiller Menu Collection

These scripts were written to get the OCR data from the Harley Spiller collection. Purpose of each file:

-all_pages.txt contains all the PIDs of the pages to have ocr performed on.
-finished_pages.txt logs all the PIDs of the pages which have been processed. (This keeps track of where to start in all_pages.txt, make sure it is empty if you want to use the script on another set of PIDs.)
-get_pages is a small script to figure out which pages need to be processed.
-ocr_processing_script does the processing, saving the data for each PID.

To use, go into ocr_processing_script and use the ocr() function in the main block to specify an output location.
