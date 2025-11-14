import psr.factory 
import pandas as pd

def create_dataframe(code,name, property,value_a,value_b):
    # code, name, porperty, value A, value B 
    data = {'code': [code],
        'name': [name],
        'property': [property],
        'value_a':[value_a],
        'value_b':[value_b]}
    df = pd.DataFrame(data)

    df_multi_index = df.set_index(['code', 'name', 'property'])

    return df_multi_index

def add_to_dataframe(type, code, name, property, value_a, value_b, dataframes):

    if type not in dataframes:
        dataframes[type] = create_dataframe(code,name, property,value_a,value_b)
    else: 
        df = dataframes[type]
        new_line = {'code':code,'name':name, 'porperty':property, 'value_a':value_a, 'value_b':value_b}
        df = df.append(new_line, ignore_index = False)

    return dataframes

def compare_studies(study_a, study_b, dataframes):

    all_objects=study_a.get_all_objects()
    for obj in all_objects:
        
        type = obj.type 
        code = obj.code
        name = obj.name

        #Check if existes in study B 
        obj_b = study_b.find_by_code(type,code)

        #No correspontet object in study B
        if len(obj_b) ==0:  
            dataframes= add_to_dataframe(type, code, name, "Removed Object", "None", "None", dataframes)
        
        #Exacly one correspontent in study b 
        elif len(obj_b)==1:
            obj_b= obj_b[0]
            for key, value in obj.as_dict().items():
                if key.startswith("Ref"): #Ignore by now
                    continue
                #Compare if the values are equal 
                value_a = value
                value_b = obj_b.get(key)
                if value_a != value_b: 
                    dataframes = add_to_dataframe(type, code, name, key, value_a, value_b, dataframes)

        #More than one correspont
        elif len(obj_b)>1:
            ref_sys_a = obj.get("RefSystem")
            for item in obj_b:
                ref_sys_b = item.get("RefSystem")
                if ref_sys_a.code == ref_sys_b.code:
                    for key, value in obj.as_dict().items():
                        if key.startswith("Ref"): #Ignore by now
                            continue
                        #Compare if the values are equal 
                        value_a = value
                        value_b = item.get(key)
                        if value_a != value_b: 
                            dataframes = add_to_dataframe(type, code, name, key, value_a, value_b, dataframes)
                else:
                    dataframes= add_to_dataframe(type, code, name, "Removed Object", "None", "None", dataframes)

    return dataframes


#Define cases path 
STUDY_A_PATH = r'Case15'
STUDY_B_PATH = r'Case15_mod'

#Load studies
study_a = psr.factory.load_study(STUDY_A_PATH)
study_b = psr.factory.load_study(STUDY_B_PATH)

dataframes = {}

print(compare_studies(study_a, study_b,dataframes))


