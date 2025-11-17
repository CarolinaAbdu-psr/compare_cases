import psr.factory 
import pandas as pd

def create_dataframe(code,name,options, property,value_a,value_b):
    # code, name, porperty, value A, value B 
    data = {'code': [code],
        'name': [name],
        'op': [options],
        'property': [property],
        'value_a':[value_a],
        'value_b':[value_b]}
    df = pd.DataFrame(data)

    df_multi_index = df.set_index(['code', 'name', 'op'])

    return df_multi_index

def add_to_dataframe(type, code, name, options, property, value_a, value_b, dataframes):

    if type not in dataframes:
        dataframes[type] = create_dataframe(code,name, options, property,value_a,value_b)
    else: 
        df = dataframes[type]
        new_line = create_dataframe(code,name,options,property,value_a,value_b)
        dataframes[type] = pd.concat([df,new_line], ignore_index = False)

    return dataframes


def compare_values(obj_source, obj_target, dataframes): 
    for key, value in obj_source.as_dict().items():
        if key.startswith("Ref"): #Ignore by now
            continue
        #Compare if the values are equal 
        value_a = value
        try: 
            value_b = obj_target.get(key)
        except :
            value_b = None

        if value_a != value_b: 
            type = obj_source.type
            code = obj_source.code
            name = obj_source.name
            dataframes = add_to_dataframe(type, code, name, "M", key, value_a, value_b, dataframes)
    
    return dataframes

def find_correspondent(obj_source, obj_target):
    ref_sys_a = obj_source.get("RefSystem")
    for item in obj_target:
        ref_sys_b = item.get("RefSystem")
        if ref_sys_a.code == ref_sys_b.code:
            return item 

def compare_studies(study_a, study_b, dataframes):

    all_objects=study_a.get_all_objects()
    study_b_visited_objects  =[]
    for obj in all_objects:
        
        type = obj.type 
        code = obj.code
        name = obj.name
        
        #Check if existes in study B 
        if code: 
            obj_b = study_b.find_by_code(type,code)
        else:
            obj_b = study_b.find_by_name(type,name)

        #No correspontet object in study B
        if len(obj_b) ==0:  
            dataframes= add_to_dataframe(type, code, name, "R", "None","None", "None", dataframes)
        
        #Exacly one correspontent in study b 
        elif len(obj_b)==1:
            dataframes = compare_values(obj,obj_b[0],dataframes)
            study_b_visited_objects.append(obj_b[0])

        #More than one correspont
        elif len(obj_b)>1:
            obj_b = find_correspondent(obj,obj_b)
            if obj_b:
                dataframes = compare_values(obj,obj_b,dataframes)
                study_b_visited_objects.append(obj_b)
            else:
                dataframes= add_to_dataframe(type, code, name, "R", "None", "None", "None", dataframes)


    #Get remaining objects of study b: 
    all_objects=study_b.get_all_objects()
    for obj in all_objects:
        print(obj)
        if obj in study_b_visited_objects:
            continue
        
        type = obj.type 
        code = obj.code
        name = obj.name

        dataframes= add_to_dataframe(type, code, name, "A", "None","None", "None", dataframes)


    return dataframes


#Define cases path 
STUDY_A_PATH = r'Case15'
STUDY_B_PATH = r'Case15_mod'

#Load studies
study_a = psr.factory.load_study(STUDY_A_PATH)
study_b = psr.factory.load_study(STUDY_B_PATH)

fuel = study_a.find_by_code("Fuel",1)[0]
study_a.remove(fuel)

fuel = study_b.find_by_code("Fuel",2)[0]
study_b.remove(fuel)

dataframes = {}

for type, df in compare_studies(study_a, study_b,dataframes).items():
    print(type)
    print(df)


