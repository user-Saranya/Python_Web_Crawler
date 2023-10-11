# Importing necessary libraries
import requests
from bs4 import BeautifulSoup
import argparse
import urllib.parse
import urllib3
import matplotlib.pyplot as plt

# Disable SSL/TLS warnings to suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set up command-line argument parser
parser = argparse.ArgumentParser(description='Web Crawler')
parser.add_argument('-u', '--url', help='Input url')
parser.add_argument('-t', '--level', help='threshold of recursion')
parser.add_argument('-o', '--output_file', help='Output file')

# Parse command-line arguments
args = parser.parse_args()

# Initializing required lists
total_links = []  # Nested list - For storing all links
internal_links = []  # Nested list - For storing all internal links
external_links = []  # Nested list - For storing all external links
types = []  # Nested list - For storing the types of all links

# Assigning variables to the input parameters
i_dep = int(args.level)
i_url = args.url
o_url = args.output_file

# Opening output file
output_file = open(o_url, "w")

# Check if depth is zero
if i_dep == 0:
    output_file.write(f"Error: Depth should be greater than zero.")
    exit(1)

# To get base domain of input url
base_domain = urllib.parse.urlparse(i_url).netloc


# Function for finding the extension of url, used for segregating files into different types
def type_of_link(url):
    # Parsing the URL
    parsed_url = urllib.parse.urlparse(url)
    # To get the path from the parsed URL
    path = parsed_url.path
    # Split the path into parts
    parts = path.split('/')
    # To get the last part (filename)
    filename = parts[-1]
    # Split the filename to get extension
    if '.' in filename:
        extension = filename.split(".")[-1]
        return extension
    else:
        # For Miscellaneous files
        return "Misc"


# Recursive crawling function
def crawl(url, depth):
    """
        Recursive function to crawl the web pages and extract links.

        Args:
            url (str): The URL to crawl.
            depth (int): The current depth of recursion.

        Returns:
            None
    """
    # Base case: Stop crawling if depth is 0
    if depth > 0:
        try:
            # Send a GET request to the URL
            response = requests.get(url, verify=False)

            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # for listing all elements in particular recursion level
            # Determine the current recursion level, here, level will be equal to current recursion level - 1
            # Here, i_dep is the input depth
            level = i_dep - depth

            # Initialize lists for current recursion level A new empty list is appended to the following lists if
            # their length is less than or equal to current recursion level
            if len(total_links) <= level:
                total_links.append([])
            if len(internal_links) <= level:
                internal_links.append([])
            if len(external_links) <= level:
                external_links.append([])
            if len(types) <= level:
                types.append([])

            # Process the page (e.g., extract information, save data, etc.)
            # Find all the links on the page
            links = soup.find_all(['a', 'img', 'script', 'link'])

            # Here, depth is reduced by one for next recursion
            depth = depth - 1

            # Fill the lists with corresponding links
            for a_link in links:
                # Extract the URL from the 'href', 'src' attributes
                if a_link.has_attr('href'):
                    next_url = a_link.get('href')
                elif a_link.has_attr('src'):
                    next_url = a_link.get('src')
                else:
                    continue

                # Construct the absolute URL by joining the base URL and the relative URL
                next_url = urllib.parse.urljoin(url, next_url)
                # Append the next_url only if it is not already present in total_links at this recursion level
                if next_url not in total_links[level]:
                    total_links[level].append(next_url)

                    # Determine the extension of next_url
                    extsn = type_of_link(next_url)

                    # Append the link's type only if it is not present already in types at this recursion level
                    if extsn not in [item[0] for item in types[level]]:
                        types[level].append([extsn, []])

                    # Check if the link is internal or external
                    next_domain = urllib.parse.urlparse(next_url).netloc
                    next_scheme = urllib.parse.urlparse(next_url).scheme

                    if next_url and (next_scheme == "http" or next_scheme == "https") and (
                            next_domain == base_domain or next_domain == ""):
                        # Recursively crawl the next URL with reduced depth
                        internal_links[level].append(next_url)
                        crawl(next_url, depth)
                    else:
                        external_links[level].append(next_url)

        except requests.exceptions.RequestException as er:
            print('Error:', er)


crawl(i_url, i_dep)

# Segregate the total_links based on their extension at each recursion level
for i in range(len(total_links)):
    for link_i in total_links[i]:
        ext_i = type_of_link(link_i)
        type_index = [x[0] for x in types[i]].index(ext_i)
        types[i][type_index][1].append(link_i)

# For output
a = len(total_links)

# For plotting the file types and their counts
rows = a // 2 + a % 2
cols = 2
fig, axs = plt.subplots(rows, cols, figsize=(8, 4 * rows), squeeze=False)
fig.suptitle('File Type Distribution for each Recursion level')

for b in range(a):
    c = b + 1
    total = len(total_links[b])
    internal = len(internal_links[b])
    external = len(external_links[b])
    output_file.write(f"At recursion level: {str(c)}\n")
    output_file.write(f"Total files found: {str(total)}\n\n")
    output_file.write("Segregating them into different types:\n")
    for type_info in types[b]:
        ext = type_info[0]
        link_list = type_info[1]
        ll = len(link_list)
        if ext == "Misc":
            output_file.write(f"\nMiscellaneous files: {str(ll)}\n")
            for link in link_list:
                output_file.write(f"{link}\n")
        else:
            output_file.write(f"\nFiles with extension '{ext}': {str(ll)}\n")
            for link in link_list:
                output_file.write(f"{link}\n")
    output_file.write(f"\n")
    output_file.write(f"Internal files found: {str(internal)}\n")
    for y in range(internal):
        output_file.write(f"{internal_links[b][y]}\n")
    output_file.write(f"\nExternal files found: {str(external)}\n")
    for z in range(external):
        output_file.write(f"{external_links[b][z]}\n")
    output_file.write(f"\n")
    labels = []
    values = []
    for element in types[b]:
        file_type = element[0]
        file_count = len(element[1])
        # Prepare data for the horizontal bar chart
        labels.append(file_type)
        values.append(file_count)
    # Plot the horizontal bar chart
    ax = axs[b // cols, b % cols]
    ax.barh(labels, values, color='orange', edgecolor='blue', height=0.7)
    ax.invert_yaxis()
    ax.set_xlabel('Count')
    ax.set_ylabel('File Type')
    ax.set_title(f'Recursion Level {b + 1}')

# If the number of recursion levels is odd, remove the last subplot to maintain a balanced layout
if a % 2 == 1:
    fig.delaxes(axs[-1, -1])

plt.tight_layout()

# Save the output file
output_file.close()

# Display the plots
plt.show()
