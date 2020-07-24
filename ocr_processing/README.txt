ocr_processing:

This script is using the Textcleaner script from ImageMagick to pre-process images by converting them into grayscale versions and removing surrounding noise making to ready for OCR.
The script then uses Google Vision API to extract text from the image and finally stores it in JSON and txt formats namely annotated_ocr.json and OCR.txt respectively in the same directory as the image.

HOW TO USE:

In the main block, set the \'91path\'92 variable to the desired path of the directory containing all the image folders. The script will recursively find the image folders from the specifies path.
