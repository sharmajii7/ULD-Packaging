import streamlit as st
import time
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
        x = st.sidebar.number_input("Enter value for x", value=7)
        y = st.sidebar.number_input("Enter value for y", value=1)
        z = st.sidebar.number_input("Enter value for z", value=4)
        d = st.sidebar.number_input("Enter value for d", value=1)
        surface_area = st.sidebar.number_input("Enter the support surface area ratio: ", min_value=0.3, max_value=1.0, step=0.1, format="%0.1f")

        if st.button("Run Assignment"):
            run_assignment(ulds, packages, k, x, y, z, d, surface_area)

def run_assignment(ulds, packages, k, x, y, z, d, s_s_a_r):
    start = time.time()

    # Sort ULDs and packages
    ulds.sort(key=lambda u: (-u['volume'], -u['weightlimit']))
    packages.sort(
        key=lambda p: (
            p['type'] != "Priority",  # Sort Priority packages first
            -(max(p['length'], p['height'], p['width'])) if p['type'] == "Priority" else -(pow(p['delaycost'], x) / ((pow(p['volume'], y) * pow(max(p['length'], p['width'], p['height']), z) * pow(p['weight'], d))))  # Sort by decreasing volume for Priority, and by decreasing delaycost for others
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
            packids=[pkg['id'] for pkg in assigned_packages],  # IDs of combined packages
            s_s_a_r=s_s_a_r
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

    uld_pack_desc = dict()

    for uld in ulds:
        already_assigned = bin_assignments.get(uld['id'], [])
        assigned_packages = [pkg for pkg in packages if pkg['id'] in already_assigned]

        spaceUtilisation(
            ulds=[uld],
            packages=assigned_packages,
            packids=[pkg['id'] for pkg in assigned_packages],
            s_s_a_r=s_s_a_r
        )
        # uld_pack_desc[uld['id']] = lines

    # st.write(f"Number of priority packages not packed: {unpacked_count}")

    non_empty_bins = sum(1 for bin_id, items in bin_assignments.items() if items)
    totcost += k * non_empty_bins

    st.subheader("Packages Not Assigned to Any ULD")

    unpackedids = []
    tot_unpacked = 0

    remaining_packages = packages[priority_count:]
    total_remaining = len(remaining_packages)

    progress_bar = st.progress(0)
    status_text = st.empty()
    
    not_assigned_ids = []

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
                packids=[pkg['id'] for pkg in assigned_packages],  # IDs of combined packages
                s_s_a_r=s_s_a_r
            )

            if unpacked_count == 0:
                bin_assignments[uld['id']].append(current_package['id'])
                assigned = True
                break

        if not assigned:
            tot_unpacked += 1
            unpackedids.append(current_package['id'])
            totcost += current_package['delaycost']
            not_assigned_ids.append(f"{current_package['id']} ")

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

        lines,fig = visualiser(
            ulds=[uld],
            packages=assigned_packages,
            packids=[pkg['id'] for pkg in assigned_packages],
            s_s_a_r=s_s_a_r
        )
        # uld_plot = st.pyplot(fig)
        alllines.extend(lines)
        # for line in uld_pack_desc[uld['id']]:
        #     st.write(line)
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
    st.download_button(
        label="Packages Not Assigned",
        data=''.join(not_assigned_ids),
        file_name='output.txt',
        mime='text/plain'
    )

if __name__ == "__main__":
    main()
