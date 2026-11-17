# DIAB-PIP-001 preparation, part 2 — covariates and identity linkage (tables and header text only)

## CDED: 69 lab records; 2 without a table row

- columns found: {'height': 'HEIGHT (M) (GE-79_Summary_Table-Demographics-MRI-Part1.csv)', 'race': 'Race (GE-79_Summary_Table-Demographics-MRI-Part1.csv)', 'group': 'Group (GE-79_Summary_Table-Demographics-MRI-Part1.csv)'}
- non-missing among people with a lab record (n=67): {'height': 67, 'race': 67, 'group': 67, 'age': 0, 'sex': 0}
- data-dictionary rows mentioning age or sex: ['Age', 'Age Range', 'Gender']
- headers with comment lines: 0; comment keys: none

Marginal label counts among people with a lab record (never split by group):

- `visit`: {'2': 67}
- `group`: {'control': 29, 'dm': 38}
- `study`: {'ge79': 67}
- `dm, non-dm, stroke`: {'dm': 38, 'non-dm': 29}
- `htn or not`: {'htn': 33, 'ntn': 30}
- `beta blockers`: {'n': 52, 'y': 15}

## GE75: 52 lab records; 0 without a table row

- columns found: {'height': 'HEIGHT (M) (GE-75_data_summary_table.csv)', 'race': 'Race (GE-75_data_summary_table.csv)', 'group': 'Group (GE-75_data_summary_table.csv)', 'age': 'age (GE-75_data_summary_table.csv)', 'sex': 'sex (GE-75_data_summary_table.csv)'}
- non-missing among people with a lab record (n=52): {'height': 52, 'race': 52, 'group': 52, 'age': 52, 'sex': 52}
- data-dictionary rows mentioning age or sex: ['Age', 'Gender']
- headers with comment lines: 0; comment keys: none

Marginal label counts among people with a lab record (never split by group):

- `group`: {'control': 6, 'dm': 46}
- `study`: {'ge75': 52}
- `dm, non-dm, stroke`: {'dm': 46, 'non-dm': 6}
- `sex`: {'female': 21, 'male': 31}
- `gender`: {}
- `htn or not`: {'htn': 18, 'ntn': 31}
- `beta blockers`: {'n': 42, 'y': 9}

## Are shared IDs the same person?

- CDED_vs_GE75: {'shared_ids': 11, 'height_comparable': 11, 'height_within_3cm': 10, 'race_comparable': 11, 'race_same': 9, 'group_comparable': 11, 'group_same': 11}
- CDED_vs_GE71: {'shared_ids': 4, 'height_comparable': 4, 'height_within_3cm': 4, 'race_comparable': 4, 'race_same': 4, 'group_comparable': 4, 'group_same': 4}
- GE75_vs_GE71: {'shared_ids': 0, 'height_comparable': 0, 'height_within_3cm': 0, 'race_comparable': 0, 'race_same': 0, 'group_comparable': 0, 'group_same': 0}

## CDED people whose age and sex exist in another dataset under the same ID

- {'cded_lab_people': 69, 'also_in_GE75_table': 10, 'also_in_GE75_lab_records': 10, 'also_in_GE71_table': 2, 'age_and_sex_recoverable_via_shared_id': 12}

