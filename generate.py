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


def load_parameters(path):
    with open(path, "r") as fp:
        d = yaml.load(fp)

    if not isinstance(d, dict):
        return []

    return list(d.keys())


def add_parameters(rolename, parameters):
    mapping1.setdefault(rolename, set())

    for parameter in parameters:
        logging.info(f"Found parameter {parameter} in {rolename}")
        mapping1[rolename].add(parameter)
        mapping2.setdefault(parameter, set()).add(rolename)


def is_defaults_file(path):
    # Ansible loads defaults/main.{yml,yaml,json}, defaults/main, and
    # every file below a defaults/main/ directory
    return re.search(r"/defaults/main(\.ya?ml|\.json)?$", path) or re.search(
        r"/defaults/main/[^/]+\.(ya?ml|json)$", path
    )


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

                if not is_defaults_file(f):
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

                logging.info(f"Analyzing {rolename} ({f})")
                add_parameters(rolename, load_parameters(f))

# Sort everything for stable output
sorted_mapping1 = {k: sorted(mapping1[k]) for k in sorted(mapping1.keys())}
sorted_mapping2 = {k: sorted(mapping2[k]) for k in sorted(mapping2.keys())}


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
