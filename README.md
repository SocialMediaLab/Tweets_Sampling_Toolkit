# About the Tweets Sampling Toolkit

The Tweets Sampling Toolkit contains a set of tools for 1) creating a random sample from massive (100M+) Tweet ID datasets, such as those available in the Social Media Lab's [COVID-19 Twitter Pandemic Archive](https://stream.covid19misinfo.org/tweet_ids) and for 2) performing [set operations](https://www.cuemath.com/algebra/operations-on-sets/) with Tweet ID datasets such as [intersection](https://en.wikipedia.org/wiki/Intersection), [difference](https://en.wikipedia.org/?title=Set_difference&redirect=not), or [union](https://en.wikipedia.org/wiki/Intersection).

The main feature of this toolkit is that it’s optimized to reliably process extremely large CSV files (multiple gigabytes) with minimal memory use. Specifically, the toolkit reads an input file one line at a time whenever possible to minimize memory use.

# Input Format / Supported File Types

This toolkit is designed to ingest any text/CSV files consisting of a list of uniformly-sized integers separated by line breaks. The first line is skipped if it's non-numeric. You can find sample input files in the [COVID-19 Twitter Pandemic Archive](https://stream.covid19misinfo.org/tweet_ids).

  

# Setup

1.  Install Python 3
    
2.  Install tqdm (progress bar utility): `pip3 install tqdm`

3.  Place the file(s) you will be working with in a directory with **tweets_sampling.py** and **external_sort.py**.
    
4.  For testing purposes, you can download and use one of the COVID-19 related datasets from [COVID-19 Twitter Pandemic Archive](https://stream.covid19misinfo.org/tweet_ids)  (Note: In the sample code below, we’re using [this file](https://doi.org/10.6084/m9.figshare.16897018).)
    
5.  Import **tweets_sampling** and create a “file manager” object as shown below:
    
```python
import tweets_sampling

ifm = tweets_sampling.id_file_manager('april_2021_COVID-19_+_Vaccines_Twitter_Streaming_Dataset.csv')
```

6.  Use the following call to confirm the number of Tweet IDs stored in the input file.
    
```python
ifm.id_count
```

# Creating Samples

## Random Samples

Use `get_random_sample()` to produce a new randomly chosen, duplicate-free list of Tweet IDs from an existing text/csv file.

Parameters:
1.  **n**: Number or percentage of Tweet IDs to include in a sample
2.  **output_file**: Relative path of a text file to store the sample
3.  **sample_mode**: Method for choosing the sample size: either "absolute" (default) or "percent" based on the total number of Tweet IDs in the input file.

Returns: An **id_file_manager** object linking to the resulting file with the sample data.

```python
# Create a sample containing 20% of our original file

percent_sample = ifm.get_random_sample( 0.2, 'percent_sample.csv', sample_mode='percent')

percent_sample.id_count

50280
```

```python
# Create a sample with 300 Tweet IDs from our first sample

absolute_sample = percent_sample.get_random_sample(300, 'absolute_sample.csv')

absolute_sample.id_count

300
```
  

## Page Samples

Use `get_page_samples()` to break a large file into multiple smaller files. This is helpful when you need to process a large dataset but don't have the resources to do it all at once.

Parameters:

1.  **page_count**: The number of output files to create.
2.  **output_file**: The relative path of resulting files. Page numbers are added to the file names (pages.csv becomes pages_0.csv, pages_1.csv, etc.). Page numbers are zero-padded as needed.

Returns: a list of **id_file_manager** objects to work with the resulting files if needed.

```python
# Split the large file into 5 subsets

pages = ifm.get_page_samples(5, 'pages.csv')
for page in pages:
	print(f'{page.file_name}: {page.id_count}')

pages_0.csv: 50280
pages_1.csv: 50280
pages_2.csv: 50280
pages_3.csv: 50280
pages_4.csv: 50281
```

# Comparing Files

This package also includes several methods for comparing the contents of two datasets and performing set operations such as [intersection](https://en.wikipedia.org/wiki/Intersection), [difference](https://en.wikipedia.org/?title=Set_difference&redirect=not), or [union](https://en.wikipedia.org/wiki/Intersection).

## Intersection

Use `get_intersection()` to create a file containing only Tweet IDs that are in both of the files.

Parameters:
1.  **file_manager**: A file manager object to compare to
2.  **output_file**: The relative path of the resulting file.
    
Returns: An **id_file_manager** object to interact with the resulting dataset.

```python
#Start by establishing a connection with two input files (further referenced as a and b objects)

a = ifm.get_random_sample(0.3, 'a.csv', sample_mode='percent')
b = ifm.get_random_sample(0.3, 'b.csv', sample_mode='percent')
```

```python
# Compare Tweet IDs stored in each file and save/return only those Tweet IDs that are stored in both datasets: a and b

intersection = a.get_intersection(b, 'intersection.csv')

intersection.id_count

22511
```

## Difference

Using `a.get_difference(b, 'difference.csv')` will create a file called 'difference.csv’ with Tweet IDs that are in a but not in  b.

Parameters:
1.  **file_manager**: A file manager object to compare to
2.  **output_file**: The relative path of the resulting file.

Returns: An **id_file_manager** object with the resulting dataset.


```python
# Get all of the IDs that are in a, but not b
difference = a.get_difference(b, 'difference.csv')

difference.id_count

52909
```

## Union

Use `a.get_union(b, 'union.csv')` to combine Tweet IDs from two datasets (referenced here as **a** and **b**) and save the resulting union in 'union.csv'. The output file will store Tweet IDs that are in either of two input files, excluding any duplicates.

Parameters:
1.  **file_manager**: An “id_file_manager” object that is linked to the dataset to compare to    
2.  **output_file**: The relative path of the resulting file.
    
Returns: An **id_file_manager** object with the resulting dataset.

```python
# Merge all Tweet IDs from dataset a and b

union = a.get_union(b, 'union.csv')

union.id_count
```

## Credit

This toolkit relies on a sort algorithm by @manangandhi7 for union, difference, and intersection operations. Learn more at [his blog](https://minimalcodes.wordpress.com/2016/05/29/sorting-large-number-of-elements-external-sort-in-cpp/) or the original [GitHub repository](https://github.com/manangandhi7/External-sort).
