HTM Performance Benchmark
=========================

# Problem Statement

This project is just an attempt to find our why HTM.java port is so slow.  

I am not telling that "the product is bad", I want to ask "please, help me to find out why it is processing about 200 records per second only?".

Thanks in advance for all those who helped. 

# Project Structure
- Folder "data" contains the dataset which was obtained from [here](https://aqsdr1.epa.gov/aqsweb/aqstmp/airdata/download_files.html#Raw) . We've taken the hourly ozone data for years 2014-2016 and "unioned" these years into one file.
- Folder "htm-java" contains an application which is an extract from our real app. It creates HTM network using the network API and processes the input rows from one_device_2015-2017.csv.
- Folder "htm-python" will contain the python implementation of the same code.  At this moment I did not do it yet, sorry. To be done soon.
