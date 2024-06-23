import yaml
import os
import re
import shutil
from datetime import datetime

homepage = "../index.mdx"
victim_dir = "../offer"
data_file = "data.yaml"
ransomware_type_data_file = "ransomware-type-info.yaml"


with open(data_file, 'r') as file:
    data = yaml.safe_load(file)

with open(ransomware_type_data_file, "r") as file:
    ransomware_type_info_data = yaml.safe_load(file)

 
# Function to parse the date, treating '??' as a high value to ensure proper sorting
def parse_date(date_str):
    if '??' in date_str:
        date_str = re.sub(r'\?\?', '32', date_str)  # Replace '??' with '32' to make it a high value
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return datetime.strptime(date_str.replace('32', '01'), "%Y-%m-%d")
    else:
        return datetime.strptime(date_str, "%Y-%m-%d")

# Sort the data by date in descending order (newest first)
sorted_data = sorted(data, key=lambda x: parse_date(x['date']), reverse=True)

# Markdown header
header = """---
title: 'Velkommen til Datainnbrudd!'
description: 'Aggregert data om cybersikkerhets hendelser i Norge'
sidebarTitle: 'Hjem'
mode: 'wide'
---\n
"""

# Define the header of the Markdown table
markdown_table = header + "| Dato | Offer | Hendelse type |\n| --- | --- | --- |\n"

# Remove the existing victim directory and create a new one
shutil.rmtree(victim_dir, ignore_errors=True)
os.makedirs(victim_dir, exist_ok=True)

# Loop over each item, append to the markdown table, and create individual MDX files
for item in sorted_data: 
    date = item.get('date')
    entity = item.get('entity')
    entity_clean = re.sub("[\\W_]+", "-", entity, re.UNICODE)
    image = item.get("image")
    summary = item.get("summary")
    references = "\n".join([f"- {reference}" for reference in item.get("reference")])
    
    
    template = f"""---
title: '{entity} - {date.replace("-", ".")}'
mode: 'wide'
---

<Frame>
<img src="/images/{image}" />
</Frame>

{summary}

<sup><i>Oppsummeringen er laget av en KI-tjeneste fra OpenAI. Innholdet er kvalitetssikret før publisering</i></sup>

## Refereranser
{references}
"""
    
    incident_type = item.get('incident-type')
    ransomware_type = item.get('ransomware-type')
    if ransomware_type:
        url = ransomware_type_info_data.get(ransomware_type)
        incident_type = f"Ransomware ([{ransomware_type}]({url}))"
    
    filename = f"{entity_clean}-{date.replace('??', 'NA')}.mdx"
    markdown_table += f"| {date} | [{entity}]({victim_dir}/{filename.replace(".mdx", "")}) | {incident_type} |\n"
    
    with open(f"{victim_dir}/{filename}", "w") as f:
        f.write(template)

# Write the markdown table to the homepage file
with open(homepage, 'w') as file:
    file.write(markdown_table)

print("Updated!")
