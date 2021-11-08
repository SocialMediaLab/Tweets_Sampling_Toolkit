# About Tweet ID Tools

The Tweet ID Tools package contains tools to help create subsets and samples of large lists of numbers, such as the Social Media Lab's [COVID-19 Twitter Streaming Dataset](https://stream.covid19misinfo.org/tweet_ids).

The methods in this package are optimized to reliably process extremely large CSV files (multiple gigabytes) with minimal memory use.

# File Types

These tools are designed for the lists of Tweet IDs in the [COVID-19 Twitter Streaming Dataset](https://stream.covid19misinfo.org/tweet_ids), but will work with any list of uniformly-sized integers separated by line breaks. The first line is skipped if it's non-numeric. The methods read these files one line at a time whenever possible to avoid memory errors. 

# Setup

1. Install Python3
2. Place the file(s) you will be working with in a directory with tweet_id_subsets.py. We will be using [this file](https://doi.org/10.6084/m9.figshare.16897018) as an example.
3. Import tweet_id_subsets and create a file manager object:


```python
import tweet_id_subsets

ifm = tweet_id_subsets.id_file_manager(
    'april_2021_COVID-19_+_Vaccines_Twitter_Streaming_Dataset.csv'
)
ifm.id_count
```




    251401



# Creating Samples
## Random Samples
Use <code>get_random_sample()</code> to produce a new randomly chosen, duplicate-free list of IDs from a file.

Parameters: 
1. <code>n</code>: Number of IDs to include in sample
2. <code>output_file</code>: Relative path of file to save sample
3. <code>sample_mode</code> (optional, default "absolute"): Method for choosing sample size - if "percent" is chosen, it will n will give the percentage of the original file to include

Returns: An <code>id_file_manager</code> for the resulting file.


```python
# Create a sample containing 20% of our original file
percent_sample = ifm.get_random_sample(
    0.2,
    'percent_sample.csv', 
    sample_mode='percent'
)
percent_sample.id_count
```




    50280




```python
# Create a sample with 300 IDs from our first sample
absolute_sample = percent_sample.get_random_sample(300, 'absolute_sample.csv')
absolute_sample.id_count
```




    300





## Page Samples
Use <code>get_page_samples()</code> to break a large file into multiple smaller files. Each ID from the original file will be present in exactly one of the resulting files. This is helpful when you need to process a large dataset but don't have the resources to do it all at once.

Parameters:
1. <code>page_count</code>: The number of output files to create.
2. <code>output_file</code>: The relative path of resulting files. Page numbers are added to the file names (<code>pages.csv</code> becomes <code>pages_0.csv</code>, <code>pages_1.csv</code>, etc.). Page numbers are zero-padded as needed.

Returns: a list of <code>id_file_manager</code> objects for the resulting files.


```python
# Split the large file into 5 subsets
pages = ifm.get_page_samples(5, 'pages.csv')

for page in pages:
    print(f'{page.file_name}: {page.id_count}')
```

    pages_0.csv: 50280
    pages_1.csv: 50280
    pages_2.csv: 50280
    pages_3.csv: 50280
    pages_4.csv: 50281


# Comparing Files
This package also includes several methods for comparing the contents of files, and creating subsets based on them. We'll create file handlers for two files to compare:


```python
a = ifm.get_random_sample(0.3, 'a.csv', sample_mode='percent')
b = ifm.get_random_sample(0.3, 'b.csv', sample_mode='percent')
```

## Intersection
Use <code>get_intersection</code> to create a file containing only tweets that are in **both** of the files.

Parameters:
1. <code>file_manager</code>: A file manager to compare to
2. <code>output_file</code>: The relative path of the resulting file.

Returns: An <code>id_file_manager</code> with the resulting dataset.


```python
# Get all of the files that are in both a and b
intersection = a.get_intersection(b, 'intersection.csv')
intersection.id_count
```




    22511



## Difference
Using <code>a.get_difference(b, 'example')</code> will create a file with all the IDs that are **in a but not in b**.

Parameters:
1. <code>file_manager</code>: A file manager to compare to
2. <code>output_file</code>: The relative path of the resulting file.

Returns: An <code>id_file_manager</code> with the resulting dataset.


```python
# Get all of the IDs that are in a, but not b
difference = a.get_difference(b, 'difference.csv')
difference.id_count
```




    52909



## Union
Use <code>get_union</code> to create a file with all the IDs that are in **either** of two files. The result will account for any overlap and will not contain duplicates.

Parameters:
1. <code>file_manager</code>: A file manager to compare to
2. <code>output_file</code>: The relative path of the resulting file.

Returns: An <code>id_file_manager</code> with the resulting dataset.


```python
# Get all of the 
union = a.get_union(b, 'union.csv')
union.id_count
```


