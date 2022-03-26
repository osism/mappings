import yaml

with open("mapping3.yml") as fp:
    data = yaml.safe_load(fp)

mapping4 = {}

for k in data:
    mapping4.setdefault(data[k], [])
    mapping4[data[k]].append(k) 

with open("mapping4.yml", "w+") as fp:
    fp.write(yaml.dump(mapping4))
