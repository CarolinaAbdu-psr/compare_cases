# Compare Cases Repositoty 

Get to SDDP cases and track the changes from case A to case B. 

The output is a folder with csv files, one for each object type.

On this csv the objcts are tracked as removed, added or moodify (property)

# v1.0 (14/11)
- Dataframes with code,name, property,value_a,value_b
- For each element case A, check the conditions: 
    - If it exist on study B 
    - If there is only one element with that code and name, check if properties changed
    - If there are more than one, get the one with teh same RefSystem and check if properties changed
- Append changes to a dataframe

# v1.1 (17/11)
- Add column OP: "R" = removed, "A" = added, "M" = modified
- Add condition: For all objects in study b, if is not on study_b_visited_objects list, add a line of added object. 

# v1.2 (17/11)
- Check Ref properties added (compare code, name and Ref System of Ref Objects list)
- Create folders with csv

# v1.3 (18/11)
- Compare dynamic properties (dataframes) and add to the modifications files the dates which values are different
- Add study object comparison 

# v1.4 (01/12)
- Replace as_dict by descriptions
- Add treatement for dataframes of properties that varies per block/scenario 

# v1.5 (15/12)
- Compare the columns names of dataframes to check which collumns are common in both dataframes
- Compare each column of common collumns of dataframes
- Fixed the static problem of static properties with dimensions

# v1.6 
- Add logging file (log.txt)

## To do list 
- Check elements that doesn't have code
