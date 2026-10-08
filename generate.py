#!/usr/bin/env python3

import glob
import logging
import os
import re

from ruamel.yaml import YAML

yaml = YAML()
yaml.indent(sequence=4, offset=2)

level = logging.INFO
logging.basicConfig(
    format="%(asctime)s - %(message)s", level=level, datefmt="%Y-%m-%d %H:%M:%S"
)

ANSIBLE_DIRECTORIES = ["/ceph-ansible", "/kolla-ansible", "/osism-ansible"]

SUMMARY_LIMIT = 50

mapping1 = {}
mapping2 = {}

for ansible_directory in ANSIBLE_DIRECTORIES:
    logging.info(f"Analyzing {ansible_directory}")
    for p in sorted([x[0] for x in os.walk(ansible_directory, followlinks=True)]):
        b = os.path.basename(p)
        if b in ["defaults"]:
            # skip integration tests of the ansible community collections
            if "tests/integration" in p:
                continue

            logging.info(f"Found {b} in {p}")

            for f in sorted(
                [
                    x
                    for x in glob.iglob(p + "**/**", recursive=True)
                    if os.path.isfile(x)
                ]
            ):
                # skip integration tests of the ansible community collections
                if "tests/integration" in f:
                    continue

                if "collections/ansible_collections" in f:
                    pattern = ".*/collections/ansible_collections/(.*)/(.*)/roles/(.*)/defaults"
                    match = re.search(pattern, f)
                    rolename = f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
                elif "galaxy/roles/" in f:
                    pattern = ".*/galaxy/roles/(.*)/defaults"
                    match = re.search(pattern, f)
                    rolename = f"{match.group(1)}"
                elif "galaxy/" in f:
                    pattern = "galaxy/(.*)/defaults"
                    match = re.search(pattern, f)
                    rolename = f"{match.group(1)}"
                else:
                    pattern = "roles/(.*)/defaults"
                    match = re.search(pattern, f)

                    if "ceph" in ansible_directory:
                        rolename = f"ceph.{match.group(1)}"
                    elif "kolla" in ansible_directory:
                        rolename = f"kolla.{match.group(1)}"
                    else:
                        rolename = f"{match.group(1)}"

                if rolename in mapping1:
                    continue

                logging.info(f"Analyzing {rolename}")

                mapping1[rolename] = []

                with open(f, "r") as fp:
                    d = yaml.load(fp)

                try:
                    for parameter in sorted(d.keys()):
                        logging.info(f"Found parameter {parameter} in {rolename}")
                        mapping1[rolename].append(parameter)

                        if parameter not in mapping2:
                            mapping2[parameter] = []
                        mapping2[parameter].append(rolename)

                except:  # noqa
                    pass

# Sort all lists in mapping1 and mapping2 for stable output
for rolename in mapping1:
    mapping1[rolename].sort()

for parameter in mapping2:
    mapping2[parameter].sort()

# Create sorted dictionaries for stable key ordering
sorted_mapping1 = {k: mapping1[k] for k in sorted(mapping1.keys())}
sorted_mapping2 = {k: mapping2[k] for k in sorted(mapping2.keys())}


def load_previous_mapping(path):
    try:
        with open(path, "r") as fp:
            return yaml.load(fp) or {}
    except FileNotFoundError:
        return {}


def limited(lines, limit=SUMMARY_LIMIT):
    if len(lines) <= limit:
        return lines
    return lines[:limit] + [f"... and {len(lines) - limit} more"]


def summarize(previous, current):
    # Printed to stdout and used as the PR body by the update-mappings
    # workflow, so every list is limited to stay well below GitHub's
    # 65,536 character limit
    sections = []

    added_roles = sorted(set(current) - set(previous))
    removed_roles = sorted(set(previous) - set(current))
    common_roles = sorted(set(current) & set(previous))

    added_parameters = [
        f"{rolename}: {parameter}"
        for rolename in common_roles
        for parameter in current[rolename]
        if parameter not in previous[rolename]
    ]
    removed_parameters = [
        f"{rolename}: {parameter}"
        for rolename in common_roles
        for parameter in previous[rolename]
        if parameter not in current[rolename]
    ]

    for title, lines in [
        (
            "Roles added",
            [f"{r} ({len(current[r])} parameters)" for r in added_roles],
        ),
        (
            "Roles removed",
            [f"{r} ({len(previous[r])} parameters)" for r in removed_roles],
        ),
        ("Parameters removed", removed_parameters),
        ("Parameters added", added_parameters),
    ]:
        if lines:
            sections.append("\n".join([f"{title} ({len(lines)}):"] + limited(lines)))

    if not sections:
        return "No changes."

    return "\n\n".join(sections)


print(summarize(load_previous_mapping("/output/mapping1.yml"), sorted_mapping1))

with open("/output/mapping1.yml", "w+") as fp:
    yaml.dump(sorted_mapping1, fp)

with open("/output/mapping2.yml", "w+") as fp:
    yaml.dump(sorted_mapping2, fp)
