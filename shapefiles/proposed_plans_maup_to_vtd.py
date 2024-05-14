import maup
import geopandas as gpd
import os
import glob

def find_shp_files(directory):
    shp_files = glob.glob(os.path.join(directory, '*.shp'))
    return shp_files

vtd_df = gpd.read_file("vtds/mi_pl2020_vtd.shp").set_index("GEOID20")
print("vtds loaded")
plans = {"congress": ["Apple v2", "Birch v2", "Final Chestnut"],
"state_house": ["Court Map", "Daisy 2", "Trillium", "Water Lily"],
"state_senate": ["Cherry v2", "Linden", "Palm"]}

for plan_type in ["state_house", "state_senate", "congress"]:
    for plan in plans[plan_type]:
        directory_path = f"proposed_plans/{plan_type}/{plan}/"
        shp_files = find_shp_files(directory_path)

        if len(shp_files) > 1:
            raise ValueError("More than one shapefile found.")

        districts = gpd.read_file(shp_files[0])
        print("districts loaded")

        # add one to reindex
        vtd_to_plan = maup.assign(vtd_df, districts.to_crs(vtd_df.crs)) + 1

        vtd_to_plan.to_csv(f"../Michigan/proposed_plans/vtd_level/{plan_type}/{plan}_vtd.csv", index=True)



# save as cvs with GEOID20,assignment columns
# save to Michigan/proposed_plans/vtd_level/plan_type
# save with {name of plan}_vtd.csv