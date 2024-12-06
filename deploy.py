import streamlit as st
import time
import plotly.graph_objects as go

import random
# from packageAssigner import packageAssigner
from visualiser import visualiser
from spaceutilisation import spaceUtilisation
from packageAssigner import packageAssigner

def parse_file(file_content):
    ulds = []
    packages = []
    k = 0
    lines = file_content.decode("utf-8").split('\n')
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


def generate_random_color():
    """Generate a random hex color."""
    return f"#{random.randint(0, 0xFFFFFF):06x}"

def parse_coordinates_from_output(file_path):
    coordinates = []

    with open(file_path, 'r') as file:
        # Skip the first line as it seems to be metadata
        next(file)

        for line in file:
            parts = line.strip().split(',') 
            if parts[1]=='NONE':
                continue
            
            # Assuming the 4th, 5th, and 6th values are x_start, y_start, z_start respectively
            x_start = float(parts[2])  # The 3rd value (index 2) is x_start
            y_start = float(parts[3])  # The 4th value (index 3) is y_start
            z_start = float(parts[4])  # The 5th value (index 4) is z_start
            x_end=float(parts[5])
            y_end=float(parts[6])
            z_end=float(parts[7])

            coordinates.append((x_start, y_start, z_start,x_end,y_end,z_end))

    return coordinates

def visualiser(ulds, packages, packids):
    fig = go.Figure()
    coordinates = parse_coordinates_from_output('output.txt')  # Get coordinates from file

    # Add ULDs as transparent 3D cuboids
    for uld in ulds:
        uld_x = [0, 0, uld['length'], uld['length'], 0, 0, uld['length'], uld['length']]
        uld_y = [0, uld['width'], uld['width'], 0, 0, uld['width'], uld['width'], 0]
        uld_z = [0, 0, 0, 0, uld['height'], uld['height'], uld['height'], uld['height']]
        
        fig.add_trace(go.Mesh3d(
            x=uld_x,
            y=uld_y,
            z=uld_z,
            color='black',
            # i=[0, 0, 0, 1, 1, 2, 2, 4, 4, 5, 6, 7],
            # j=[1, 2, 4, 3, 5, 3, 6, 5, 6, 6, 7, 3],
            # k=[2, 4, 5, 2, 3, 6, 4, 6, 7, 7, 3, 5],
            opacity=0,
            name=f"ULD: {uld['id']}",
            # flatshading=True
        ))

    
    for idx, (x_start, y_start, z_start,x_end,y_end,z_end) in enumerate(coordinates):
        color = generate_random_color()
        
        
        # Assume the package size (length, width, height) is predefined or passed to the function
        # length, width, height = packages[idx]['length'], packages[idx]['width'], packages[idx]['height']
        
        # x_end, y_end, z_end = x_start + length, y_start + width, z_start + height

        pkg_x = [x_start, x_start, x_end, x_end, x_start, x_start, x_end, x_end]
        pkg_y = [y_start, y_end, y_end, y_start, y_start, y_end, y_end, y_start]
        pkg_z = [z_start, z_start, z_start, z_start, z_end, z_end, z_end, z_end]



        fig.add_trace(go.Mesh3d(
            x=pkg_x,
            y=pkg_y,
            z=pkg_z,
            color=color,
            i=[0, 0, 0, 1, 1, 2, 2, 4, 4, 5, 6, 7],
            j=[1, 2, 4, 3, 5, 3, 6, 5, 6, 6, 7, 3],
            k=[2, 4, 5, 2, 3, 6, 4, 6, 7, 7, 3, 5],
            opacity=1,
            name=f"Package {packids[idx]}",
            # flatshading=True
        ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Length'),
            yaxis=dict(title='Width'),
            zaxis=dict(title='Height'),
        ),
        title="ULD and Package 3D Visualization"
    )
    
    return fig


def main():
    st.title("Package Assignment and ULD Optimization")

    st.write("""
    This application assigns packages to Unit Load Devices (ULDs) based on various parameters.
    """)

    # Upload input file
    uploaded_file = st.file_uploader("Choose an input file", type=["txt"])
    if uploaded_file is not None:
        ulds, packages, k = parse_file(uploaded_file.read())

        # Input parameters
        st.sidebar.header("Sorting Parameters")
        x = st.sidebar.number_input("Enter value for x", value=5)
        y = st.sidebar.number_input("Enter value for y", value=2)
        z = st.sidebar.number_input("Enter value for z", value=1)
        w = st.sidebar.number_input("Enter value for w", value=1)
        d = st.sidebar.number_input("Enter value for d", value=1)

        if st.button("Run Assignment"):
            run_assignment(ulds, packages, k, x, y, z, w, d)



def run_assignment(ulds, packages, k, x, y, z, w, d):
    start = time.time()

    # Sort ULDs and packages
    ulds.sort(key=lambda u: (-u['volume'], -u['weightlimit']))
    packages.sort(
        key=lambda p: (
            p['type'] != "Priority",
            -(max(p['length'], p['height'], p['width'])) if p['type'] == "Priority" else -(pow(p['delaycost'], x) / (pow(p['volume'], y) * pow(p['weight'], z)))
        )
    )
    packids = [pkg['id'] for pkg in packages]

    # Count Priority packages
    priority_count = sum(1 for pkg in packages if pkg['type'] == "Priority")
    priority_packages = [pkg for pkg in packages if pkg['type'] == "Priority"]
    priority_packids = [pkg['id'] for pkg in priority_packages]

    totcost = 0

    st.subheader("Space Utilization by Priority Packages")

    bin_assignments = {}

    for uld in ulds:
        bin_assignments[uld['id']] = []

    unpacked_count = 0

    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, current_package in enumerate(priority_packages):
        assigned = False

        progress_bar.progress((idx + 1) / priority_count)
        status_text.text(f"Assigning priority package {current_package['id']} ({idx + 1}/{priority_count})")

        for uld in ulds:
            already_assigned = bin_assignments.get(uld['id'], [])
            assigned_packages = [pkg for pkg in packages if pkg['id'] in already_assigned]

            assigned_packages.append(current_package)

            unpacked_count = packageAssigner(
            ulds=[uld],  # Use the current ULD
            packages=assigned_packages,  # Include already assigned + current package
            packids=[pkg['id'] for pkg in assigned_packages]  # IDs of combined packages
        )

            if unpacked_count == 0:
                bin_assignments[uld['id']].append(current_package['id'])  # Update the assignments
                assigned = True
                break  # No need to check further ULDs for this package

        if not assigned:
            unpacked_count += 1
            st.warning(f"Priority package {current_package['id']} could not be assigned to any ULD.")

    progress_bar.empty()
    status_text.empty()

    for uld in ulds:
        already_assigned = bin_assignments.get(uld['id'], [])
        assigned_packages = [pkg for pkg in packages if pkg['id'] in already_assigned]

        spaceUtilisation(
            ulds=[uld],
            packages=assigned_packages,
            packids=[pkg['id'] for pkg in assigned_packages]
        )

    st.write(f"Number of priority packages not packed: {unpacked_count}")

    non_empty_bins = sum(1 for bin_id, items in bin_assignments.items() if items)
    totcost += k * non_empty_bins

    st.subheader("Packages Not Assigned to Any ULD")

    unpackedids = []
    tot_unpacked = 0

    remaining_packages = packages[priority_count:]
    total_remaining = len(remaining_packages)

    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, current_package in enumerate(remaining_packages):
        assigned = False

        progress_bar.progress((idx + 1) / total_remaining)
        status_text.text(f"Assigning package {current_package['id']} ({idx + 1}/{total_remaining})")

        for uld in ulds:
            already_assigned = bin_assignments.get(uld['id'], [])
            assigned_packages = [pkg for pkg in packages if pkg['id'] in already_assigned]

            assigned_packages.append(current_package)

            unpacked_count = packageAssigner(
                ulds=[uld],  # Use the current ULD
                packages=assigned_packages,  # Include already assigned + current package
                packids=[pkg['id'] for pkg in assigned_packages]  # IDs of combined packages
            )

            if unpacked_count == 0:
                bin_assignments[uld['id']].append(current_package['id'])
                assigned = True
                break

        if not assigned:
            tot_unpacked += 1
            unpackedids.append(current_package['id'])
            totcost += current_package['delaycost']
            st.write(f"{current_package['id']}", end=", ")

    progress_bar.empty()
    status_text.empty()

    tot_packed = len(packages) - tot_unpacked
    firstline = f"{totcost},{tot_packed},{non_empty_bins}\n"

    st.subheader("Overall Space Utilization")

    alllines = []

    for pkg_id in unpackedids:
        line = f"{pkg_id},NONE,-1,-1,-1,-1,-1,-1\n"
        alllines.append(line)
    fig = None
    for uld in ulds:
        already_assigned = bin_assignments.get(uld['id'], [])
        assigned_packages = [pkg for pkg in packages if pkg['id'] in already_assigned]

        fig = visualiser(
            ulds=[uld],
            packages=assigned_packages,
            packids=[pkg['id'] for pkg in assigned_packages],
        )
        st.plotly_chart(fig)

        # uld_plot = st.pyplot(fig)
        # alllines.extend(lines)
        # time.sleep(0.5)
        # uld_plot.empty()

        # Display visualization (assuming visualiser returns a plot or image)
        # For example, if visualiser returns a Matplotlib figure:
        # fig = visualiser(...)
        # st.pyplot(fig)

    st.write(f"Total cost: {totcost}")
    st.write(f"Total unpacked items: {tot_unpacked}")

    stop = time.time()
    st.write(f"Time Taken: {stop - start} seconds")

    alllines = sorted(alllines, key=lambda x: int(x.split(',')[0].split('-')[1]))
    output_content = firstline + ''.join(alllines)
    
    # Provide a download link for the output
    st.download_button(
        label="Download Output",
        data=output_content,
        file_name='output.txt',
        mime='text/plain'
    )

if __name__ == "__main__":
    main()
