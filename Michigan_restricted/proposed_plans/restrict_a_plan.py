import csv 
import sys



# # create a list of nodes in required districts
districts = {"house_1":[1,7,8,10,11,12,14,2,3,4,6,9,13],
"house_2":[1,7,8,10,11,12,14,2,3,4,5,6,9,13,16],
"senate":[1,3,6,8,10,11,2,7]}

plans = {"state_house": ["MI-HD-2022_vtd.csv"],#["Court Map", "Daisy 2", "Peony", "Trillium", "Water Lily", "MI-HD-2022_vtd.csv"],
"state_senate": ["MI-SD-2022_vtd.csv"]}#["Cherry v2", "Linden", "Palm", "MI-SD-2022_vtd.csv"]}

for plan_type in districts.keys():
    print(plan_type)
    if "house" in plan_type:
        og_plan_name = "state_house"
        
    else:
        og_plan_name = "state_senate"

    for plan in plans[og_plan_name]:
        print(plan)
        proposed_plan_dir = f"/cluster/tufts/mggg/cdonna01/MI_effective/Michigan/proposed_plans/vtd_level/{og_plan_name}"
        # load the VTD to district assignment
        data = []
        file_name = f"{proposed_plan_dir}/{plan}_vtd.csv" if ".csv" not in plan else f"{proposed_plan_dir}/{plan}"
        with open(file_name, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for i, row in enumerate(csv_reader):
                if i>0:
                    if int(row[1]) in districts[plan_type]:
                        data.append(row)
                else:
                    data.append(row)

        # save to csv
        # data should be list of lists
        restricted_plan_dir = f"/cluster/tufts/mggg/cdonna01/MI_effective/Michigan_restricted/proposed_plans/vtd_level/{plan_type}"
        file_name = f"{restricted_plan_dir}/{plan}_vtd.csv" if ".csv" not in plan else f"{restricted_plan_dir}/{plan}"
        with open(file_name, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerows(data)
