def parse_input_file(filename):
    ulds = []
    packages = []
    k = 0
    with open(filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith("K"):
                k = int(line.split('=')[1].split(',')[0].strip())
                continue
            if line.startswith("ULD") or line.startswith("Package"):
                continue
            if line.startswith("U"):
                parts = line.split(',')
                ulds.append({
                    'id': parts[0],
                    'length': int(parts[1]),
                    'width': int(parts[2]),
                    'height': int(parts[3]),
                    'weightlimit': int(parts[4]),
                    'volume': int(parts[1]) * int(parts[2]) * int(parts[3]),
                })
            if line.startswith("P"):
                parts = line.split(',')
                # if(parts[5] == 'Priority'):
                #     continue
                packages.append({
                    'id': parts[0],
                    'length': int(parts[1]),
                    'width': int(parts[2]),
                    'height': int(parts[3]),
                    'weight': int(parts[4]),
                    'type': parts[5],
                    'delaycost': int(parts[6]) if parts[6] != '-' else 0,
                    'volume': int(parts[1]) * int(parts[2]) * int(parts[3]),
                })
    return ulds, packages, k

def parse_output_file(filepath):
    packages_packed = []
    packages_not_packed = []
    with open(filepath,'r') as f:
        lines = f.readlines()
        line1 = lines[0].strip().split(',')
        cost = int(line1[0])
        uld_with_priority_packages = int(line1[2])
        total_packages_packed = int(line1[1])

        for i in range(len(lines)):
            if(i == 0):
                continue
            lines[i] = lines[i].strip().split(',')
            if(lines[i][1] == 'NONE'):
                packages_not_packed.append({
                    'id' : lines[i][0]
                })
            else:
                packages_packed.append({
                    'id' : lines[i][0],
                    'uld' : lines[i][1],
                    'start' : (lines[i][2],lines[i][3],lines[i][4]),
                    'end' : (lines[i][5],lines[i][6],lines[i][7])
                })

        return cost,uld_with_priority_packages,total_packages_packed, packages_packed,packages_not_packed

def check_clearance(c1, c2):
    (x1_l, y1_l, z1_l), (x1_max, y1_max, z1_max) = c1
    (x2_l, y2_l, z2_l), (x2_max, y2_max, z2_max) = c2
    if int(x1_max) <= int(x2_l):
        return 1
    elif int(x2_max) <= int(x1_l):
        return 1
    elif int(y1_max) <= int(y2_l):
        return 1
    elif int(y2_max) <= int(y1_l):
        return 1
    elif int(z1_max) <= int(z2_l):
        return 1
    elif int(z2_max) <= int(z1_l): 
        return 1

    return 0


def check_all_overlaps(packed_packages):
    for i in range(len(packed_packages)):
        for j in range(i+1,len(packed_packages)):
            if(packed_packages[i]['uld'] == packed_packages[j]['uld']):
                if not check_clearance(((packed_packages[i]['start']),(packed_packages[i]['end'])),((packed_packages[j]['start']),(packed_packages[j]['end']))):
                    print(packed_packages[i]['start'],packed_packages[i]['end'])
                    print(packed_packages[j]['start'],packed_packages[j]['end'])
                    print(packed_packages[i]['id'],packed_packages[j]['id'])
                    return False
    return True

def check_all_priority(inp_items,outp_items):
    packed = []
    priority_present = []
    for y in outp_items:
        packed.append(y['id'])
    for x in inp_items:
        if(x['type'] == 'Priority'):
            priority_present.append(x['id'])
    for x in priority_present:
        if x not in packed:
            print(x)
            return False
    return True

def calc_cost(packages,packages_not_packed,k,uld_with_priority_packages):
    delay_costs = {}
    cost = k*uld_with_priority_packages
    for x in packages:
        if(x['type'] == 'Economy'):
            delay_costs[x['id']] = x['delaycost']
    for y in packages_not_packed:
        cost+=delay_costs[y['id']]

    return cost

def check_weight_limit(packages,packages_packed,ulds):
    uld_weights = {}
    weight_map = {}
    for x in packages:
        weight_map[x['id']] = x['weight']
    for x in packages_packed:
        if x['id'] in uld_weights:
            uld_weights[x['uld']] += weight_map[x['id']]
        else:
            uld_weights[x['uld']] = weight_map[x['id']]
    for x in ulds:
        if(x['weightlimit']<uld_weights[x['id']]):
            return False
        
    return True

filename = "Challange_FedEx.txt"
ulds, packages, k = parse_input_file(filename)
packids = []
ulds.sort(key=lambda u: -u['volume'])
packages.sort(key=lambda p: (p['type'] != "Priority", -p['delaycost']))
packids = [pkg['id'] for pkg in packages]
cost,uld_with_priority_packages,total_packages_packed,packages_packed,packages_not_packed = parse_output_file('output.txt')

print(calc_cost(packages,packages_not_packed,k,uld_with_priority_packages))
print(check_weight_limit(packages,packages_packed,ulds))
print(check_all_priority(packages,packages_packed))
print(check_all_overlaps(packages_packed))