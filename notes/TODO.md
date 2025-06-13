# Ideer

- Kompetanse bygges stein på stein, nye temaer øker kompetansen selv om man har lav score. Hvordan visualiserer vi kumulativ kompetanse?
  - UI med stein på stein?
  - Achievments?

# Datamodell

![Data Model](data_model.png 'Database Schema Diagram')

# Pattern for feide_id:

feide_id pattern for School:
fc:org:kakrafoon.kommune.no:unit:NO987654321

feide_id pattern for teaching group (the "u" is for "undervisningsgruppe"):
fc:org:kakrafoon.kommune.no:<u>:NO987654321:<3a-matte>:2000-07-01:2100-06-30"

feide_id for basis group (the "b" is for "basissgruppe"):
fc:org:kakrafoon.kommune.no:<b>:NO987654321:<3a>:2000-07-01:2100-06-30"

Feide_id for User:
feide:<username>@feide.osloskolen.no

# Links

https://www.udir.no/om-udir/data/kl06-grep/
https://github.com/Utdanningsdirektoratet/KL06-LK20-public/wiki/Swagger
https://docs.feide.no/reference/apis/groups_api/group_types/pse_teaching.html
