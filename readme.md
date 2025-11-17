# Compare Cases Repositoty 

Get to SDDP cases and track the changes from case A to case B. 

The output is a folder with csv files, one for each object type.

On this csv the objcts are tracked as removed, added or moodify (property)

# v0 (14/11)
- Dataframes with code,name, property,value_a,value_b
- For each element case A, check the conditions: 
    - If it exist on study B 
    - If there is only one element with that code and name, check if properties changed
    - If there are more than one, get the one with teh same RefSystem and check if properties changed
- Append changes to a dataframe

# v1 (17/11)
- Add column OP: "R" = removed, "A" = added, "M" = modified
- Add condition: For all objects in study b, if is not on study_b_visited_objects list, add a line of added object. 

# v2 (17/11)
- Check Ref properties added (compare code, name and Ref System of Ref Objects list)


## To do list 

- Check elements that doesn't have code
- Create folders with csv
