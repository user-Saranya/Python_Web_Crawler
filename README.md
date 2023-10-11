
# Web Crawler

## Project Overview

Web Crawler is a Python program that recursively searches and indexes web links from a given website. It finds all unique referenced web links within the same domain, categorizes them by type, and provides information about the total number of files found at each recursion level.

## Features

- Accepts a website link as a command line argument.
- Recursively crawls and finds web links within the same domain.
- Organizes links into different file types (e.g., HTML, CSS, JavaScript, images).
- Generates horizontal bar graphs to visualize file counts at each recursion level.

## Usage

To run the web crawler, use the following command:

```bash
python3 web-crawler.py -u http://www.example.com -t 5 -o output.txt
