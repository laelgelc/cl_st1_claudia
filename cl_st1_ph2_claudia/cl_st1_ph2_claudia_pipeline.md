# Corpus Linguistics - Study 1 - Phase 2 - Claudia

Run the commands from the project phase directory, e.g.:

```text
cl_st1_ph2_claudia/
```

## 1. Tag the corpus

```shell
python tag.py
```

Output: `corpus/05_tagged/<group>/`

## 2. Extract key lemmas by group

```shell
python keylemmas.py \
  --input corpus/07_tagged \
  --output corpus/08_keylemmas \
  --cutoff 3
```

Output: `corpus/06_keylemmas/<group>.tsv`

## 3. Select a stratified keyword set

```shell
python select_kws_stratified.py \
    --per-decade 50 \
    --max-total 20000
```

Output: `corpus/07_kw_selected/keywords.txt

```shell
=== Decade Keyword Quotas ===
2000   → 50 keywords max
2010   → 50 keywords max
2020   → 50 keywords max
=============================

2000   → selected 45/50 from 45 available POSKW lemmas
2010   → selected 12/50 from 12 available POSKW lemmas
2020   → selected 23/50 from 23 available POSKW lemmas

Total consolidated keywords before de-duplication: 80
Unique keywords after de-duplication: 80
Duplicates removed: 0

Final unique keywords written to: corpus/09_kw_selected/keywords.txt
Final unique keyword count: 80
```

## 4. Build binary keyword columns

```shell
rm -rf columns columns_clean
```

```shell
python columns.py
```

Outputs:
- `columns/`
- `columns_clean/`
- `file_ids.txt`
- `index_keywords.txt`

## 5. Merge columns into the SAS counts matrix

```shell
python merge_columns.py
```

Output: `sas/counts.txt`

## 6. Generate SAS format files

```shell
python sas_formats.py
```

Outputs:

- sas/word_labels_format.sas
- sas/word_labels_full_format.sas
- other SAS helper format files

## 7. Run SAS

## 8. Build factor loading lists

```shell
python factor_lists.py
```

Output: factors/

## 9. Calculate corpus size summaries

```shell
python corpus_size.py
```

Output: `corpus_size/corpus_size.tsv`

## 10. Generate LaTeX/TikZ boxplots

```shell
cd latex_boxplots
```

```shell
python latex_boxplots.py
```

Output: `latex_boxplots/slides/`

```shell
cd ..
```

## 11. Generate LaTeX ANOVA table

```shell
python latex_anova_table.py
```

Output: `latex_tables/anova_decade.tex`

## 12. Generate LaTeX example extracts

```shell
python examples.py
```

Output: `examples/`

## 13. Generate score-details report

```shell
python score_details.py
```

Output: `examples/score_details.txt`

## 14. Generate plaintext example extracts

```shell
python examples_txt.py
```

Output: `examples_txt/`

## 15. Build interpretation prompts

```shell
python interpretation_prompts.py
```

Output: `interpretation/input/`

## 16. Submit interpretation prompts to GPT

```shell
python generate_interpretation_gpt.py \
    --input interpretation/input \
    --output interpretation/output \
    --model gpt-5.6-sol \
    --workers 4
```
Output: `interpretation/output/`
