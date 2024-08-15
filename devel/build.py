import yaml
import os
import re
import shutil
from datetime import datetime
from feedgen.feed import FeedGenerator
import pytz

homepage = "index.mdx"
victim_dir = "offer"
data_file = "devel/data.yaml"
incident_context_file = "devel/incident-context.yaml"
rss_feed_file = "feed.xml"

header = """---
title: 'Velkommen til Datainnbrudd!'
description: 'Aggregert data om cybersikkerhets hendelser i Norge'
sidebarTitle: 'Hjem'
mode: 'wide'
---\n
"""

markdown_table = header + "| Dato | Offer | Hendelse type |\n|:--- |:--- |:--- |\n"


# Function to parse the date, treating '??' as a high value to ensure proper sorting
def parse_date(date_str):
    date_str = re.compile(r"\?\?").sub("32", date_str)  # Replace '??' with '32' to make it a high value
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return datetime.strptime(date_str.replace("32", "01"), "%Y-%m-%d")


with open(data_file, "r") as file:
    data = yaml.safe_load(file)

with open(incident_context_file, "r") as file:
    ransomware_type_info_data = yaml.safe_load(file)

# Sort the data by date in descending order (newest first)
sorted_data = sorted(data, key=lambda x: parse_date(x['date']), reverse=True)

# Remove the existing victim directory and create a new one
shutil.rmtree(victim_dir, ignore_errors=True)
os.makedirs(victim_dir, exist_ok=True)

fg = FeedGenerator()
fg.title("Datainnbrudd Feed")
fg.link(href="https://datainnbrudd.no", rel="self")
fg.description("RSS feed for aggregert data om cybersikkerhets hendelser i Norge")

# Helps us fetch the correct winter/summer time zone
oslo_tz = pytz.timezone('Europe/Oslo')

# Loop over each item, append to the markdown table, and create individual MDX files
for item in sorted_data: 
    date = item.get('date')
    entity = item.get('entity')
    entity_clean = re.sub("[\\W_]+", "-", entity, re.UNICODE)
    image = item.get("image")
    summary = item.get("summary")
    incident_type = item.get('incident-type')
    references = "\n".join([f"- {reference}" for reference in item.get("reference")])
    ai_notice = "<sup><i>Oppsummeringen er laget av en KI-tjeneste fra OpenAI basert på kildene nedenfor. Innholdet er kvalitetssikret før publisering.</i></sup>" if item.get("ai") else ""
    template = f"""---
title: '{entity}'
mode: 'wide'
'og:title': '{entity} - Datainnbrudd.no'
---

<Frame>
<img src="/images/{image}" noZoom/>
</Frame>

{summary}

{ai_notice}

## Kilder
{references}
"""
    
    if incident_context:= item.get("incident-context"):
        url = ransomware_type_info_data.get(incident_context)
        incident_type = f"{incident_type} ([{incident_context}]({url}))"
    
    filename = f"{entity_clean}-{date.replace('??', 'NA')}.mdx"
    markdown_table += f"| {date} | [{entity}]({victim_dir}/{filename.replace(".mdx", "")}) | {incident_type} |\n"
   
    fe = fg.add_entry()
    date = item.get('date')
    entity = item.get('entity')
    entity_clean = re.sub("[\\W_]+", "-", entity, re.UNICODE)
    summary = item.get("summary")
    incident_type = item.get('incident-type')
    
    fe.title(f"{entity} ({incident_type})")
    fe.link(href=f"https://datainnbrudd.no/{victim_dir}/{entity_clean}-{date.replace('??', 'NA')}")
    fe.description(summary)

    parsed_date = parse_date(date)
    localized_date = oslo_tz.localize(parsed_date)
    fe.pubDate(localized_date)
   
    
    with open(f"{victim_dir}/{filename}", "w") as f:
        f.write(template)

# Write the markdown table to the homepage file
with open(homepage, "w") as file:
    file.write(markdown_table)

# Write the RSS file
fg.rss_file(rss_feed_file)

print("Updated!")

