import psr.factory 
import pandas as pd
import os 
import shutil

def create_dataframe(code,name,options, property,date, value_a,value_b):
    """Creates a dataframe with the collumns from the instances"""
    
    data = {'code': [code],
        'name': [name],
        'op': [options],
        'property': [property],
        'date': [date],
        'value_a':[value_a],
        'value_b':[value_b]}
    df = pd.DataFrame(data)

    df_multi_index = df.set_index(['code', 'name', 'op'])

    return df_multi_index

def add_to_dataframe(type, code, name, options, property,date, value_a, value_b, dataframes):
    """Add a new row to a dataframe of selected object"""

    if type not in dataframes:
        dataframes[type] = create_dataframe(code,name, options, property,date, value_a,value_b)
    else: 
        df = dataframes[type]
        new_line = create_dataframe(code,name,options,property,date, value_a,value_b)
        dataframes[type] = pd.concat([df,new_line], ignore_index = False)

    return dataframes

def compare_references(ref_list_source, ref_list_target):
    "Return if two references obejcts are the same"
    for item_source in ref_list_source:
        match = False 
        for item_target in ref_list_target:
            match_name = item_source.name == item_target.name 
            match_code = item_source.code == item_target.code
            try:  
                match_system = item_source.get("RefSystem")[0].code == item_target.get("RefSystem")[0].code
            except:
                match_system = True
            match = match_name and match_code and match_system
            if match: 
                break 
        if not match: # If the item_source are not in ref target list, the objects re different 
            return False
    return match

def normalize_references(obj, key):
    """Normalize references to always be a list"""
    ref_value = obj.get(key)
    # Empty reference
    if ref_value is None:
        return []
    # Refernce is not a list
    if not isinstance(ref_value, list):
        return [ref_value]
    return ref_value

def compare_static_values(obj_source, obj_target, key, dataframes):
    """Compare static properties of two objects"""

    try:
        obj_type = obj_source.type 
        code = obj_source.code 
        name = obj_source.name 
    except:
        obj_type = "Study Object"
        code = ""
        name = ""
    
    value_a = None
    value_b = None
    try: 
        value_a = obj_target.get(key)
        value_b = obj_target.get(key)
    except:
        pass 
        
    if value_a != value_b: 
        print(f"{key}: Values different (Static) {value_a}, {value_b}")
        # Register modification of static values
        dataframes = add_to_dataframe(obj_type, code, name, "M", key, "01/01/1900 ", value_a, value_b, dataframes)
        
    return dataframes

def compare_dynamic_values(obj_source, obj_target, key, dataframes):
    """Compare dynamic properties (dataframes) such as Thermal Plants Installed Capacity modifications"""
    try:
        obj_type = obj_source.type 
        code = obj_source.code 
        name = obj_source.name 
    except:
        obj_type = "Study Object"
        code = ""
        name = ""
    
    try:
        #Compare two dataframes
        df_a = obj_source.get_df(key)
        df_b = obj_target.get_df(key)
        df_compare = df_a.compare(df_b) #Dataframe only with the diferences between two dataframes 
        print(df_compare)

    except Exception as e:
        print(f"Error comparing dynamic value {key}: {e}")
        return dataframes

    for index, row in df_compare.iterrows():
            # Add each difference to a row at the modification dataframe
            for col_block in {col for col in row.index.get_level_values(0) if col.startswith(f"{key}(")}: #Iterate between dataframes with more than 1 block
                date = str(index)
                value_a = row[(col_block,"self")]
                value_b = row[(col_block,"other")]
                dataframes = add_to_dataframe(obj_type, code, name, "M", key, date, value_a, value_b, dataframes)

    return dataframes

def find_correspondent(obj_source, obj_target):
    "Get the object with the same system"
    ref_sys_a = obj_source.get("RefSystem")
    for item in obj_target:
        ref_sys_b = item.get("RefSystem")
        if ref_sys_a.code == ref_sys_b.code:
            return item 
    return None


def compare_objects(obj_source, obj_target, dataframes): 
    """Compare two objects property by property"""

    # Get all properties of obj_source
    for key in obj_source.descriptions().keys():

        # Define object type, code, and name, with exeception for study object
        try:
            type = obj_source.type 
            code = obj_source.code 
            name = obj_source.name 
        except:
            type = "Study Object"
            code = ""
            name = ""
        
        if obj_source.description(key).is_reference() and type!= "Study Object": 

            # Normalize objects to always be a list 
            ref_list_source = normalize_references(obj_source, key)
            ref_list_target = normalize_references(obj_target, key)

            # If reference is empty 
            if not ref_list_source and not ref_list_target:
                continue
                
            # Call compare_references function to check if the objects are the same
            match = compare_references(ref_list_source, ref_list_target)

            # If refences objects are not the same, add modification on dataframe
            if not match: 
                print("Different references found")
                dataframes = add_to_dataframe(type, code, name, "M", key, "",ref_list_source, ref_list_target, dataframes)
            continue 

        #Compare if the other properties are equal (static and dynamic)
        description = obj_target.description(key)
        if description is not None: 

            if not description.is_dynamic(): 
                dataframes = compare_static_values(obj_source, obj_target, key, dataframes)

            else: 
                dataframes = compare_dynamic_values(obj_source, obj_target, key, dataframes)

    return dataframes


def compare_studies(study_a, study_b, dataframes):

    # Compare all objects from study_a with objcts from study_b
    all_objects=study_a.get_all_objects()
    study_b_visited_objects  =[]
    for obj in all_objects:
        
        try:
            type = obj.type 
            code = obj.code 
            name = obj.name 
        except:
            type = "Study Object"
            code = ""
            name = ""
        
        #Get correspondet in study B 
        obj_b = study_b.find_by_code(type,code)
      
        #No correspontet object in study B
        if len(obj_b) ==0:  
            dataframes= add_to_dataframe(type, code, name, "R", "None","None","None", "None", dataframes)
        
        #Exacly one correspontent in study b 
        elif len(obj_b)==1:
            dataframes = compare_objects(obj,obj_b[0],dataframes)
            study_b_visited_objects.append(obj_b[0])

        #More than one correspont
        elif len(obj_b)>1:
            obj_b = find_correspondent(obj,obj_b)
            if obj_b:
                dataframes = compare_objects(obj,obj_b,dataframes)
                study_b_visited_objects.append(obj_b)
            else:
                dataframes= add_to_dataframe(type, code, name, "R", "None","None","None", "None", dataframes)


    #Get remaining objects of study b: 
    all_objects=study_b.get_all_objects()
    for obj in all_objects:
        if obj in study_b_visited_objects:
            continue
        
        type = obj.type 
        code = obj.code
        name = obj.name

        dataframes= add_to_dataframe(type, code, name, "A", "None","None","None", "None", dataframes)

    #Compare study object 
    dataframes = compare_objects(study_a,study_b, dataframes)

    return dataframes


def save__dataframes(dataframes,output_dir):

    os.makedirs(output_dir, exist_ok=True)

    for filename, df in compare_studies(study_a, study_b,dataframes).items():

        df = df.fillna("None")

        csv_name = f"{filename}.csv"
        path = os.path.join(output_dir, csv_name)

        # Save dataframe to CSV
        df.to_csv(path, index=True)
        
        print(f"Saved {path}")

if __name__== "__main__":
    #Define cases path 
    STUDY_A_PATH = r'Case15'
    STUDY_B_PATH = r'Case15_mod'

    #Load studies
    study_a = psr.factory.load_study(STUDY_A_PATH)
    study_b = psr.factory.load_study(STUDY_B_PATH)

    # Set dataframes dict and output_dir
    dataframes = {}
    output_dir = "comparison_results"

    # Remove existents results
    if os.path.exists(output_dir) and os.path.isdir(output_dir):
        for item in os.listdir(output_dir):
            item_path = os.path.join(output_dir, item)

            if os.path.isfile(item_path):
                os.remove(item_path)  
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  

        print(f"Previous results from '{output_dir}' were deleted")

    save__dataframes(dataframes,output_dir)



