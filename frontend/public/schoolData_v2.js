export const data = {
  "students": [
    // Grade 4 students - 8 total
    {
      "id": "pia-eriksen",
      "name": "Pia Eriksen",
      "age": 10,
      "groupIds": ["4A", "norwegian-4", "math-4", "english-4"],
      "goalIds": ["goal-01", "goal-02", "goal-03", "goal-11", "goal-21", "goal-31", "goal-97"]
    },
    {
      "id": "camilla-hovberg",
      "name": "Camilla Hovberg",
      "age": 10,
      "groupIds": ["4A", "norwegian-4", "math-4", "science-4"],
      "goalIds": ["goal-04", "goal-12", "goal-22", "goal-41"]
    },
    {
      "id": "anders-solberg",
      "name": "Anders Solberg",
      "age": 10,
      "groupIds": ["4A", "norwegian-4", "english-4"],
      "goalIds": ["goal-05", "goal-13", "goal-32"]
    },
    {
      "id": "markus-berg",
      "name": "Markus Berg",
      "age": 10,
      "groupIds": ["4A", "math-4", "science-4"],
      "goalIds": ["goal-06", "goal-23", "goal-42"]
    },
    {
      "id": "emma-pedersen",
      "name": "Emma Pedersen",
      "age": 10,
      "groupIds": ["4B", "norwegian-4", "math-4", "english-4", "science-4"],
      "goalIds": ["goal-07", "goal-14", "goal-24", "goal-33", "goal-43"]
    },
    {
      "id": "thomas-lie",
      "name": "Thomas Lie",
      "age": 10,
      "groupIds": ["4B", "norwegian-4", "math-4"],
      "goalIds": ["goal-08", "goal-15", "goal-25"]
    },
    {
      "id": "sofie-hansen",
      "name": "Sofie Hansen",
      "age": 10,
      "groupIds": ["4B", "english-4", "science-4"],
      "goalIds": ["goal-09", "goal-34", "goal-44"]
    },
    {
      "id": "jonas-johansen",
      "name": "Jonas Johansen",
      "age": 10,
      "groupIds": ["4B", "norwegian-4", "english-4", "science-4"],
      "goalIds": ["goal-10", "goal-16", "goal-35", "goal-45"]
    },

    // Grade 5 students - 7 total (removed 4 students from 5C)
    {
      "id": "tony-lupin",
      "name": "Tony Lupin",
      "age": 11,
      "groupIds": ["5A", "norwegian-5", "math-5"],
      "goalIds": ["goal-51", "goal-61", "goal-71"]
    },
    {
      "id": "sara-kahn",
      "name": "Sara Kahn",
      "age": 11,
      "groupIds": ["5A", "norwegian-5", "math-5", "english-5"],
      "goalIds": ["goal-52", "goal-62", "goal-72", "goal-81"]
    },
    {
      "id": "erik-olsen",
      "name": "Erik Olsen",
      "age": 11,
      "groupIds": ["5A", "english-5", "science-5"],
      "goalIds": ["goal-53", "goal-82", "goal-91"]
    },
    {
      "id": "hanna-nilsen",
      "name": "Hanna Nilsen",
      "age": 11,
      "groupIds": ["5A", "norwegian-5", "english-5", "science-5"],
      "goalIds": ["goal-54", "goal-63", "goal-83", "goal-92"]
    },
    {
      "id": "mats-bakken",
      "name": "Mats Bakken",
      "age": 11,
      "groupIds": ["5B", "math-5", "science-5"],
      "goalIds": ["goal-55", "goal-73", "goal-93"]
    },
    {
      "id": "linnea-strand",
      "name": "Linnea Strand",
      "age": 11,
      "groupIds": ["5B", "norwegian-5", "math-5", "english-5", "science-5"],
      "goalIds": ["goal-56", "goal-64", "goal-74", "goal-84", "goal-94"]
    },
    {
      "id": "jakob-dahl",
      "name": "Jakob Dahl",
      "age": 11,
      "groupIds": ["5B", "norwegian-5", "english-5"],
      "goalIds": ["goal-57", "goal-65", "goal-85"]
    }
  ],
  "groups": [
    // Basis groups
    {
      "id": "4A",
      "name": "4A",
      "type": "basis",
      "grade": 4,
      "teacherIds": ["teacher-01", "teacher-02", "teacher-03", "teacher-04", "teacher-05"]
    },
    {
      "id": "4B",
      "name": "4B",
      "type": "basis",
      "grade": 4,
      "teacherIds": ["teacher-06", "teacher-07", "teacher-08", "teacher-09"]
    },
    {
      "id": "5A",
      "name": "5A",
      "type": "basis",
      "grade": 5,
      "teacherIds": ["teacher-11", "teacher-12", "teacher-13", "teacher-14", "teacher-15"]
    },
    {
      "id": "5B",
      "name": "5B",
      "type": "basis",
      "grade": 5,
      "teacherIds": ["teacher-16", "teacher-17", "teacher-18", "teacher-19"]
    },

    // Teaching groups - Grade 4
    {
      "id": "norwegian-4",
      "name": "Norsk",
      "type": "teaching",
      "grade": 4,
      "teacherIds": ["teacher-01", "teacher-03", "teacher-05"]
    },
    {
      "id": "math-4",
      "name": "Matte",
      "type": "teaching",
      "grade": 4,
      "teacherIds": ["teacher-02", "teacher-04", "teacher-10"]
    },
    {
      "id": "english-4",
      "name": "Engelsk",
      "type": "teaching",
      "grade": 4,
      "teacherIds": ["teacher-05", "teacher-07"]
    },
    {
      "id": "science-4",
      "name": "Naturfag",
      "type": "teaching",
      "grade": 4,
      "teacherIds": ["teacher-06", "teacher-08", "teacher-09", "teacher-10"]
    },

    // Teaching groups - Grade 5
    {
      "id": "norwegian-5",
      "name": "Norsk",
      "type": "teaching",
      "grade": 5,
      "teacherIds": ["teacher-11", "teacher-13", "teacher-15", "teacher-17", "teacher-19"]
    },
    {
      "id": "math-5",
      "name": "Matte",
      "type": "teaching",
      "grade": 5,
      "teacherIds": ["teacher-12", "teacher-14", "teacher-16"]
    },
    {
      "id": "english-5",
      "name": "Engelsk",
      "type": "teaching",
      "grade": 5,
      "teacherIds": ["teacher-15", "teacher-17"]
    },
    {
      "id": "science-5",
      "name": "Naturfag",
      "type": "teaching",
      "grade": 5,
      "teacherIds": ["teacher-18", "teacher-19", "teacher-20"]
    }
  ],
  "teachers": [
    // Grade 4 teachers - 10
    {
      "id": "teacher-01",
      "name": "Lars Hansen",
      "gradeAssignment": 4
    },
    {
      "id": "teacher-02",
      "name": "Maria Kemp",
      "gradeAssignment": 4
    },
    {
      "id": "teacher-03",
      "name": "Jens Giovanni",
      "gradeAssignment": 4
    },
    {
      "id": "teacher-04",
      "name": "Ilhan Berisha",
      "gradeAssignment": 4
    },
    {
      "id": "teacher-05",
      "name": "Silje Bakken",
      "gradeAssignment": 4
    },
    {
      "id": "teacher-06",
      "name": "Ole Nordmann",
      "gradeAssignment": 4
    },
    {
      "id": "teacher-07",
      "name": "Kari Eriksen",
      "gradeAssignment": 4
    },
    {
      "id": "teacher-08",
      "name": "Thomas Berg",
      "gradeAssignment": 4
    },
    {
      "id": "teacher-09",
      "name": "Lise Støre",
      "gradeAssignment": 4
    },
    {
      "id": "teacher-10",
      "name": "Per Jensen",
      "gradeAssignment": 4
    },

    // Grade 5 teachers - 10
    {
      "id": "teacher-11",
      "name": "Nina Holm",
      "gradeAssignment": 5
    },
    {
      "id": "teacher-12",
      "name": "Anders Lie",
      "gradeAssignment": 5
    },
    {
      "id": "teacher-13",
      "name": "Ingrid Pettersen",
      "gradeAssignment": 5
    },
    {
      "id": "teacher-14",
      "name": "Bjørn Solberg",
      "gradeAssignment": 5
    },
    {
      "id": "teacher-15",
      "name": "Hanne Moen",
      "gradeAssignment": 5
    },
    {
      "id": "teacher-16",
      "name": "Geir Iversen",
      "gradeAssignment": 5
    },
    {
      "id": "teacher-17",
      "name": "Mona Strand",
      "gradeAssignment": 5
    },
    {
      "id": "teacher-18",
      "name": "Jan Dahl",
      "gradeAssignment": 5
    },
    {
      "id": "teacher-19",
      "name": "Astrid Karlsen",
      "gradeAssignment": 5
    },
    {
      "id": "teacher-20",
      "name": "Kristian Johnsen",
      "gradeAssignment": 5
    }
  ],
  "goals": [
    // Goals for 4A group
    {
      "id": "goal-01",
      "title": "Bidrar i samtaler",
      "description": "Eleven bidrar i samtaler med læreren og medelever.",
      "groupId": "4A",
    },
    {
      "id": "goal-02",
      "title": "Vaske hendene",
      "description": "Eleven skal kunne vaske hendene selvstendig.",
      "groupId": "4A",
    },
    {
      "id": "goal-03",
      "title": "Gi uttrykk for behov",
      "description": "Eleven skal kunne gi uttrykk for behov og basale følelser ved bruk av riktige ord.",
      "groupId": "4A",
    },
    {
      "id": "goal-04",
      "title": "Sitte stille",
      "description": "Eleven skal kunne sitte rolig i samlingsstunder.",
      "groupId": "4A",
    },
    {
      "id": "goal-05",
      "title": "Vente på tur",
      "description": "Eleven kan vente på tur i gruppeaktiviteter.",
      "groupId": "4A",
    },
    {
      "id": "goal-06",
      "title": "Følge instruksjoner",
      "description": "Eleven kan følge instruksjoner fra lærer.",
      "groupId": "4A",
    },
    {
      "id": "goal-07",
      "title": "Samarbeid",
      "description": "Eleven viser evne til samarbeid med andre elever.",
      "groupId": "4B",
    },
    {
      "id": "goal-08",
      "title": "Orden i sekken",
      "description": "Eleven holder orden i skolesekken og tar vare på egne ting.",
      "groupId": "4B",
    },
    {
      "id": "goal-09",
      "title": "Rekke opp hånden",
      "description": "Eleven rekker opp hånden og venter på ordet.",
      "groupId": "4B",
    },
    {
      "id": "goal-10",
      "title": "Møte forberedt",
      "description": "Eleven møter forberedt til timene.",
      "groupId": "4B",
    },

    // Goals for Norwegian-4
    {
      "id": "goal-11",
      "title": "Kan skrive navnet sitt",
      "description": "Eleven kan skrive navnet sitt med blyant og papir.",
      "groupId": "norwegian-4",
    },
    {
      "id": "goal-12",
      "title": "Lese enkle tekster",
      "description": "Eleven kan lese enkle tekster med flyt.",
      "groupId": "norwegian-4",
    },
    {
      "id": "goal-13",
      "title": "Skrive enkle setninger",
      "description": "Eleven kan skrive enkle setninger med riktig tegnsetting.",
      "groupId": "norwegian-4",
    },
    {
      "id": "goal-14",
      "title": "Alfabetet",
      "description": "Eleven kan alfabetet og alfabetisere ord.",
      "groupId": "norwegian-4",
    },
    {
      "id": "goal-15",
      "title": "Diftonger",
      "description": "Eleven kan bruke diftonger i skrift.",
      "groupId": "norwegian-4",
    },
    {
      "id": "goal-16",
      "title": "Gjenfortelle",
      "description": "Eleven kan gjenfortelle hovedinnholdet i tekster.",
      "groupId": "norwegian-4",
    },

    // Goals for Math-4
    {
      "id": "goal-21",
      "title": "Telle til 100",
      "description": "Eleven kan telle til 100.",
      "groupId": "math-4",
    },
    {
      "id": "goal-22",
      "title": "Addisjon",
      "description": "Eleven kan legge sammen tall til 100.",
      "groupId": "math-4",
    },
    {
      "id": "goal-23",
      "title": "Subtraksjon",
      "description": "Eleven kan trekke fra tall opp til 100.",
      "groupId": "math-4",
    },
    {
      "id": "goal-24",
      "title": "Multiplikasjon",
      "description": "Eleven kan gangetabellene 1-5.",
      "groupId": "math-4",
    },
    {
      "id": "goal-25",
      "title": "Geometriske former",
      "description": "Eleven kjenner grunnleggende geometriske former.",
      "groupId": "math-4",
    },

    // Goals for English-4
    {
      "id": "goal-31",
      "title": "Hilsener",
      "description": "Eleven kan enkle måter å hilse på engelsk.",
      "groupId": "english-4",
    },
    {
      "id": "goal-32",
      "title": "Farger",
      "description": "Eleven kan navnet på farger på engelsk.",
      "groupId": "english-4",
    },
    {
      "id": "goal-33",
      "title": "Tall",
      "description": "Eleven kan telle til 20 på engelsk.",
      "groupId": "english-4",
    },
    {
      "id": "goal-34",
      "title": "Enkle spørsmål",
      "description": "Eleven kan stille og svare på enkle spørsmål på engelsk.",
      "groupId": "english-4",
    },
    {
      "id": "goal-35",
      "title": "Dyr",
      "description": "Eleven kan navnet på vanlige dyr på engelsk.",
      "groupId": "english-4",
    },

    // Goals for Science-4
    {
      "id": "goal-41",
      "title": "Årstider",
      "description": "Eleven kan forklare årstidene i Norge.",
      "groupId": "science-4",
    },
    {
      "id": "goal-42",
      "title": "Planter",
      "description": "Eleven kan navngi deler av en plante.",
      "groupId": "science-4",
    },
    {
      "id": "goal-43",
      "title": "Kroppen",
      "description": "Eleven kjenner til grunnleggende organer i kroppen.",
      "groupId": "science-4",
    },
    {
      "id": "goal-44",
      "title": "Materialer",
      "description": "Eleven kan skille mellom ulike materialer.",
      "groupId": "science-4",
    },
    {
      "id": "goal-45",
      "title": "Vann",
      "description": "Eleven kan beskrive vannets kretsløp.",
      "groupId": "science-4",
    },

    // Goals for 5A, 5B
    {
      "id": "goal-51",
      "title": "Gruppearbeid",
      "description": "Eleven kan samarbeide effektivt i grupper.",
      "groupId": "5A",
    },
    {
      "id": "goal-52",
      "title": "Muntlige presentasjoner",
      "description": "Eleven kan holde korte muntlige presentasjoner.",
      "groupId": "5A",
    },
    {
      "id": "goal-53",
      "title": "Tidsplanlegging",
      "description": "Eleven kan planlegge arbeidstiden sin.",
      "groupId": "5A",
    },
    {
      "id": "goal-54",
      "title": "Selvstendig arbeid",
      "description": "Eleven kan arbeide selvstendig over tid.",
      "groupId": "5A",
    },
    {
      "id": "goal-55",
      "title": "Digitale ferdigheter",
      "description": "Eleven viser grunnleggende digitale ferdigheter.",
      "groupId": "5B",
    },
    {
      "id": "goal-56",
      "title": "Ansvar for egne ting",
      "description": "Eleven tar ansvar for egne eiendeler og lekser.",
      "groupId": "5B",
    },
    {
      "id": "goal-57",
      "title": "Konstruktiv tilbakemelding",
      "description": "Eleven kan gi konstruktive tilbakemeldinger til medelever.",
      "groupId": "5B",
    },

    // Goals for Norwegian-5
    {
      "id": "goal-61",
      "title": "Lesestrategi",
      "description": "Eleven kan bruke ulike lesestrategier.",
      "groupId": "norwegian-5",
    },
    {
      "id": "goal-62",
      "title": "Sammensatte tekster",
      "description": "Eleven kan skrive sammensatte tekster med innledning og avslutning.",
      "groupId": "norwegian-5",
    },
    {
      "id": "goal-63",
      "title": "Grammatikk",
      "description": "Eleven kan grunnleggende grammatiske begreper.",
      "groupId": "norwegian-5",
    },
    {
      "id": "goal-64",
      "title": "Skrifttyper",
      "description": "Eleven mestrer både håndskrift og tastatur.",
      "groupId": "norwegian-5",
    },
    {
      "id": "goal-65",
      "title": "Muntlig formidling",
      "description": "Eleven kan formidle kunnskap muntlig med struktur.",
      "groupId": "norwegian-5",
    },
    {
      "id": "goal-66",
      "title": "Tekstforståelse",
      "description": "Eleven forstår fag- og skjønnlitterære tekster.",
      "groupId": "norwegian-5",
    },
    {
      "id": "goal-67",
      "title": "Kildebruk",
      "description": "Eleven kan oppgi kilder i enkle oppgaver.",
      "groupId": "norwegian-5",
    },

    // Goals for Math-5
    {
      "id": "goal-71",
      "title": "Multiplikasjon opp til 10",
      "description": "Eleven behersker gangetabellene 1-10.",
      "groupId": "math-5",
    },
    {
      "id": "goal-72",
      "title": "Divisjon",
      "description": "Eleven kan dele tall med énsifrede tall.",
      "groupId": "math-5",
    },
    {
      "id": "goal-73",
      "title": "Brøk",
      "description": "Eleven forstår begrepet brøk og kan regne med enkle brøker.",
      "groupId": "math-5",
    },
    {
      "id": "goal-74",
      "title": "Desimaltall",
      "description": "Eleven kan regne med enkle desimaltall.",
      "groupId": "math-5",
    },
    {
      "id": "goal-75",
      "title": "Måling",
      "description": "Eleven kan måle lengde, areal og volum.",
      "groupId": "math-5",
    },
    {
      "id": "goal-76",
      "title": "Koordinatsystem",
      "description": "Eleven kan plassere punkter i et koordinatsystem.",
      "groupId": "math-5",
    },
    {
      "id": "goal-77",
      "title": "Statistikk",
      "description": "Eleven kan lage og tolke enkel statistikk.",
      "groupId": "math-5",
    },

    // Goals for English-5
    {
      "id": "goal-81",
      "title": "Samtale",
      "description": "Eleven kan føre en enkel samtale på engelsk.",
      "groupId": "english-5",
    },
    {
      "id": "goal-82",
      "title": "Skrive tekst",
      "description": "Eleven kan skrive korte, sammenhengende tekster på engelsk.",
      "groupId": "english-5",
    },
    {
      "id": "goal-83",
      "title": "Leseforståelse",
      "description": "Eleven kan lese og forstå tilpassede tekster på engelsk.",
      "groupId": "english-5",
    },
    {
      "id": "goal-84",
      "title": "Grammatikk",
      "description": "Eleven kan bruke grunnleggende grammatiske strukturer.",
      "groupId": "english-5",
    },
    {
      "id": "goal-85",
      "title": "Ordforråd",
      "description": "Eleven har et variert ordforråd innen kjente temaer.",
      "groupId": "english-5",
    },
    {
      "id": "goal-86",
      "title": "Kultur",
      "description": "Eleven kjenner til kulturelle aspekter ved engelskspråklige land.",
      "groupId": "english-5",
    },
    {
      "id": "goal-87",
      "title": "Uttale",
      "description": "Eleven har tydelig og forståelig uttale på engelsk.",
      "groupId": "english-5",
    },

    // Goals for Science-5
    {
      "id": "goal-91",
      "title": "Solsystem",
      "description": "Eleven kan beskrive solsystemet og planetene.",
      "groupId": "science-5",
    },
    {
      "id": "goal-92",
      "title": "Økosystem",
      "description": "Eleven forstår begrepet økosystem og næringskjeder.",
      "groupId": "science-5",
    },
    {
      "id": "goal-93",
      "title": "Energiformer",
      "description": "Eleven kan forklare ulike energiformer.",
      "groupId": "science-5",
    },
    {
      "id": "goal-94",
      "title": "Teknikk",
      "description": "Eleven kan planlegge og bygge enkle tekniske konstruksjoner.",
      "groupId": "science-5",
    },
    {
      "id": "goal-95",
      "title": "Menneskets organer",
      "description": "Eleven kan beskrive funksjonene til menneskets hovedorganer.",
      "groupId": "science-5",
    },
    {
      "id": "goal-96",
      "title": "Klimasoner",
      "description": "Eleven kan beskrive ulike klimasoner på jorden.",
      "groupId": "science-5",
    },
    {
      "id": "goal-97",
      "title": "Bruke spørreord",
      "description": "Eleven kan stille spørsmål med korrekt bruk av spørreord.",
      "groupId": "norwegian-4",
    }
  ],
  "observations": [
    // 4th grade student - 7 obs per goal - increasing mastery
    {
      "id": "obs-pia-g01-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 15,
      "groupId": "4A",
      "goalId": "goal-01",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g01-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 25,
      "groupId": "4A",
      "goalId": "goal-01",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g01-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 38,
      "groupId": "4A",
      "goalId": "goal-01",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g01-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 52,
      "groupId": "4A",
      "goalId": "goal-01",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g01-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 68,
      "groupId": "4A",
      "goalId": "goal-01",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g01-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 82,
      "groupId": "4A",
      "goalId": "goal-01",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g01-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 95,
      "groupId": "4A",
      "goalId": "goal-01",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g01-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 15,
      "groupId": "4A",
      "goalId": "goal-01",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g97-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 22,
      "groupId": "norwegian-4",
      "goalId": "goal-97",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g97-2",
      "createdAt": "2022-01-15T10:00:00Z",
      "masteryValue": 39,
      "groupId": "norwegian-4",
      "goalId": "goal-97",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g97-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 25,
      "groupId": "norwegian-4",
      "goalId": "goal-97",
      "studentId": "pia-eriksen"
    },
    // 4th grade student - 7 obs per goal - flat mastery
    {
      "id": "obs-emma-g07-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 45,
      "groupId": "4B",
      "goalId": "goal-07",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g07-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 48,
      "groupId": "4B",
      "goalId": "goal-07",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g07-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 52,
      "groupId": "4B",
      "goalId": "goal-07",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g07-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 49,
      "groupId": "4B",
      "goalId": "goal-07",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g07-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 51,
      "groupId": "4B",
      "goalId": "goal-07",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g07-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 53,
      "groupId": "4B",
      "goalId": "goal-07",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g07-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 50,
      "groupId": "4B",
      "goalId": "goal-07",
      "studentId": "emma-pedersen"
    },

    // 4th grade student - 7 obs per goal - erratic mastery
    {
      "id": "obs-jonas-g10-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 35,
      "groupId": "4B",
      "goalId": "goal-10",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g10-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 58,
      "groupId": "4B",
      "goalId": "goal-10",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g10-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 42,
      "groupId": "4B",
      "goalId": "goal-10",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g10-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 75,
      "groupId": "4B",
      "goalId": "goal-10",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g10-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 65,
      "groupId": "4B",
      "goalId": "goal-10",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g10-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 82,
      "groupId": "4B",
      "goalId": "goal-10",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g10-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 68,
      "groupId": "4B",
      "goalId": "goal-10",
      "studentId": "jonas-johansen"
    },

    // 5th grade student - 9 obs per goal - increasing mastery
    {
      "id": "obs-sara-g52-1",
      "createdAt": "2020-06-15T10:00:00Z",
      "masteryValue": 10,
      "groupId": "5A",
      "goalId": "goal-52",
      "studentId": "sara-kahn"
    },
    {
      "id": "obs-sara-g52-2",
      "createdAt": "2021-01-20T10:00:00Z",
      "masteryValue": 18,
      "groupId": "5A",
      "goalId": "goal-52",
      "studentId": "sara-kahn"
    },
    {
      "id": "obs-sara-g52-3",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 28,
      "groupId": "5A",
      "goalId": "goal-52",
      "studentId": "sara-kahn"
    },
    {
      "id": "obs-sara-g52-4",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 42,
      "groupId": "5A",
      "goalId": "goal-52",
      "studentId": "sara-kahn"
    },
    {
      "id": "obs-sara-g52-5",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 58,
      "groupId": "5A",
      "goalId": "goal-52",
      "studentId": "sara-kahn"
    },
    {
      "id": "obs-sara-g52-6",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 69,
      "groupId": "5A",
      "goalId": "goal-52",
      "studentId": "sara-kahn"
    },
    {
      "id": "obs-sara-g52-7",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 77,
      "groupId": "5A",
      "goalId": "goal-52",
      "studentId": "sara-kahn"
    },
    {
      "id": "obs-sara-g52-8",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 88,
      "groupId": "5A",
      "goalId": "goal-52",
      "studentId": "sara-kahn"
    },
    {
      "id": "obs-sara-g52-9",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 95,
      "groupId": "5A",
      "goalId": "goal-52",
      "studentId": "sara-kahn"
    },

    // 5th grade student - 9 obs per goal - flat mastery
    {
      "id": "obs-mats-g55-1",
      "createdAt": "2020-06-15T10:00:00Z",
      "masteryValue": 62,
      "groupId": "5B",
      "goalId": "goal-55",
      "studentId": "mats-bakken"
    },
    {
      "id": "obs-mats-g55-2",
      "createdAt": "2021-01-20T10:00:00Z",
      "masteryValue": 65,
      "groupId": "5B",
      "goalId": "goal-55",
      "studentId": "mats-bakken"
    },
    {
      "id": "obs-mats-g55-3",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 61,
      "groupId": "5B",
      "goalId": "goal-55",
      "studentId": "mats-bakken"
    },
    {
      "id": "obs-mats-g55-4",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 63,
      "groupId": "5B",
      "goalId": "goal-55",
      "studentId": "mats-bakken"
    },
    {
      "id": "obs-mats-g55-5",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 66,
      "groupId": "5B",
      "goalId": "goal-55",
      "studentId": "mats-bakken"
    },
    {
      "id": "obs-mats-g55-6",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 64,
      "groupId": "5B",
      "goalId": "goal-55",
      "studentId": "mats-bakken"
    },
    {
      "id": "obs-mats-g55-7",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 67,
      "groupId": "5B",
      "goalId": "goal-55",
      "studentId": "mats-bakken"
    },
    {
      "id": "obs-mats-g55-8",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 68,
      "groupId": "5B",
      "goalId": "goal-55",
      "studentId": "mats-bakken"
    },
    {
      "id": "obs-mats-g55-9",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 65,
      "groupId": "5B",
      "goalId": "goal-55",
      "studentId": "mats-bakken"
    },

    // 5th grade student - 9 obs per goal - decreasing mastery
    {
      "id": "obs-oli-g61-1",
      "createdAt": "2020-06-15T10:00:00Z",
      "masteryValue": 85,
      "groupId": "norwegian-5",
      "goalId": "goal-61",
      "studentId": "oliver-berg"
    },
    {
      "id": "obs-oli-g61-2",
      "createdAt": "2021-01-20T10:00:00Z",
      "masteryValue": 82,
      "groupId": "norwegian-5",
      "goalId": "goal-61",
      "studentId": "oliver-berg"
    },
    {
      "id": "obs-oli-g61-3",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 78,
      "groupId": "norwegian-5",
      "goalId": "goal-61",
      "studentId": "oliver-berg"
    },
    {
      "id": "obs-oli-g61-4",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 72,
      "groupId": "norwegian-5",
      "goalId": "goal-61",
      "studentId": "oliver-berg"
    },
    {
      "id": "obs-oli-g61-5",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 65,
      "groupId": "norwegian-5",
      "goalId": "goal-61",
      "studentId": "oliver-berg"
    },
    {
      "id": "obs-oli-g61-6",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 58,
      "groupId": "norwegian-5",
      "goalId": "goal-61",
      "studentId": "oliver-berg"
    },
    {
      "id": "obs-oli-g61-7",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 48,
      "groupId": "norwegian-5",
      "goalId": "goal-61",
      "studentId": "oliver-berg"
    },
    {
      "id": "obs-oli-g61-8",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 42,
      "groupId": "norwegian-5",
      "goalId": "goal-61",
      "studentId": "oliver-berg"
    },
    {
      "id": "obs-oli-g61-9",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 35,
      "groupId": "norwegian-5",
      "goalId": "goal-61",
      "studentId": "oliver-berg"
    },
    {
      "id": "obs-pia-g02-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 12,
      "groupId": "4A",
      "goalId": "goal-02",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g02-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 25,
      "groupId": "4A",
      "goalId": "goal-02",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g02-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 40,
      "groupId": "4A",
      "goalId": "goal-02",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g02-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 57,
      "groupId": "4A",
      "goalId": "goal-02",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g02-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 70,
      "groupId": "4A",
      "goalId": "goal-02",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g02-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 85,
      "groupId": "4A",
      "goalId": "goal-02",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g02-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 93,
      "groupId": "4A",
      "goalId": "goal-02",
      "studentId": "pia-eriksen"
    },

    // Goal-03 - erratic pattern
    {
      "id": "obs-pia-g03-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 28,
      "groupId": "4A",
      "goalId": "goal-03",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g03-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 45,
      "groupId": "4A",
      "goalId": "goal-03",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g03-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 37,
      "groupId": "4A",
      "goalId": "goal-03",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g03-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 60,
      "groupId": "4A",
      "goalId": "goal-03",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g03-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 53,
      "groupId": "4A",
      "goalId": "goal-03",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g03-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 72,
      "groupId": "4A",
      "goalId": "goal-03",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g03-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 65,
      "groupId": "4A",
      "goalId": "goal-03",
      "studentId": "pia-eriksen"
    },

    // Goal-11 - increasing pattern
    {
      "id": "obs-pia-g11-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 20,
      "groupId": "norwegian-4",
      "goalId": "goal-11",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g11-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 32,
      "groupId": "norwegian-4",
      "goalId": "goal-11",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g11-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 48,
      "groupId": "norwegian-4",
      "goalId": "goal-11",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g11-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 61,
      "groupId": "norwegian-4",
      "goalId": "goal-11",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g11-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 75,
      "groupId": "norwegian-4",
      "goalId": "goal-11",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g11-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 88,
      "groupId": "norwegian-4",
      "goalId": "goal-11",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g11-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 97,
      "groupId": "norwegian-4",
      "goalId": "goal-11",
      "studentId": "pia-eriksen"
    },

    // Goal-21 - flat pattern
    {
      "id": "obs-pia-g21-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 52,
      "groupId": "math-4",
      "goalId": "goal-21",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g21-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 54,
      "groupId": "math-4",
      "goalId": "goal-21",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g21-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 50,
      "groupId": "math-4",
      "goalId": "goal-21",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g21-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 53,
      "groupId": "math-4",
      "goalId": "goal-21",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g21-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 55,
      "groupId": "math-4",
      "goalId": "goal-21",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g21-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 58,
      "groupId": "math-4",
      "goalId": "goal-21",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g21-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 56,
      "groupId": "math-4",
      "goalId": "goal-21",
      "studentId": "pia-eriksen"
    },

    // Goal-31 - decreasing pattern
    {
      "id": "obs-pia-g31-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 86,
      "groupId": "english-4",
      "goalId": "goal-31",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g31-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 78,
      "groupId": "english-4",
      "goalId": "goal-31",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g31-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 72,
      "groupId": "english-4",
      "goalId": "goal-31",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g31-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 65,
      "groupId": "english-4",
      "goalId": "goal-31",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g31-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 58,
      "groupId": "english-4",
      "goalId": "goal-31",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g31-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 52,
      "groupId": "english-4",
      "goalId": "goal-31",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-g31-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 45,
      "groupId": "english-4",
      "goalId": "goal-31",
      "studentId": "pia-eriksen"
    },

    // Camilla Hovberg - goals (goal-04, goal-12, goal-22, goal-41)
    // Goal-04 - increasing pattern
    {
      "id": "obs-camilla-g04-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 18,
      "groupId": "4A",
      "goalId": "goal-04",
      "studentId": "camilla-hovberg"
    },
    {
      "id": "obs-camilla-g04-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 34,
      "groupId": "4A",
      "goalId": "goal-04",
      "studentId": "camilla-hovberg"
    },
    {
      "id": "obs-camilla-g04-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 45,
      "groupId": "4A",
      "goalId": "goal-04",
      "studentId": "camilla-hovberg"
    },
    {
      "id": "obs-camilla-g04-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 58,
      "groupId": "4A",
      "goalId": "goal-04",
      "studentId": "camilla-hovberg"
    },
    {
      "id": "obs-camilla-g04-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 69,
      "groupId": "4A",
      "goalId": "goal-04",
      "studentId": "camilla-hovberg"
    },
    {
      "id": "obs-camilla-g04-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 82,
      "groupId": "4A",
      "goalId": "goal-04",
      "studentId": "camilla-hovberg"
    },
    {
      "id": "obs-camilla-g04-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 94,
      "groupId": "4A",
      "goalId": "goal-04",
      "studentId": "camilla-hovberg"
    },

    // Goal-12 - flat pattern
    {
      "id": "obs-camilla-g12-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 42,
      "groupId": "norwegian-4",
      "goalId": "goal-12",
      "studentId": "camilla-hovberg"
    },
    {
      "id": "obs-camilla-g12-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 45,
      "groupId": "norwegian-4",
      "goalId": "goal-12",
      "studentId": "camilla-hovberg"
    },
    {
      "id": "obs-camilla-g12-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 44,
      "groupId": "norwegian-4",
      "goalId": "goal-12",
      "studentId": "camilla-hovberg"
    },
    {
      "id": "obs-camilla-g12-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 47,
      "groupId": "norwegian-4",
      "goalId": "goal-12",
      "studentId": "camilla-hovberg"
    },
    {
      "id": "obs-camilla-g12-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 48,
      "groupId": "norwegian-4",
      "goalId": "goal-12",
      "studentId": "camilla-hovberg"
    },
    {
      "id": "obs-camilla-g12-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 46,
      "groupId": "norwegian-4",
      "goalId": "goal-12",
      "studentId": "camilla-hovberg"
    },
    {
      "id": "obs-camilla-g12-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 49,
      "groupId": "norwegian-4",
      "goalId": "goal-12",
      "studentId": "camilla-hovberg"
    },

    // Goal-22 for Camilla - increasing pattern
    {
      "id": "obs-camilla-g22-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 14,
      "groupId": "math-4",
      "goalId": "goal-22",
      "studentId": "camilla-hovberg"
    },
    {
      "id": "obs-camilla-g22-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 28,
      "groupId": "math-4",
      "goalId": "goal-22",
      "studentId": "camilla-hovberg"
    },
    {
      "id": "obs-camilla-g22-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 42,
      "groupId": "math-4",
      "goalId": "goal-22",
      "studentId": "camilla-hovberg"
    },
    {
      "id": "obs-camilla-g22-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 56,
      "groupId": "math-4",
      "goalId": "goal-22",
      "studentId": "camilla-hovberg"
    },
    {
      "id": "obs-camilla-g22-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 70,
      "groupId": "math-4",
      "goalId": "goal-22",
      "studentId": "camilla-hovberg"
    },
    {
      "id": "obs-camilla-g22-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 85,
      "groupId": "math-4",
      "goalId": "goal-22",
      "studentId": "camilla-hovberg"
    },
    {
      "id": "obs-camilla-g22-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 92,
      "groupId": "math-4",
      "goalId": "goal-22",
      "studentId": "camilla-hovberg"
    },

    // Goal-41 for Camilla - erratic pattern
    {
      "id": "obs-camilla-g41-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 28,
      "groupId": "science-4",
      "goalId": "goal-41",
      "studentId": "camilla-hovberg"
    },
    {
      "id": "obs-camilla-g41-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 45,
      "groupId": "science-4",
      "goalId": "goal-41",
      "studentId": "camilla-hovberg"
    },
    {
      "id": "obs-camilla-g41-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 32,
      "groupId": "science-4",
      "goalId": "goal-41",
      "studentId": "camilla-hovberg"
    },
    {
      "id": "obs-camilla-g41-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 51,
      "groupId": "science-4",
      "goalId": "goal-41",
      "studentId": "camilla-hovberg"
    },
    {
      "id": "obs-camilla-g41-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 48,
      "groupId": "science-4",
      "goalId": "goal-41",
      "studentId": "camilla-hovberg"
    },
    {
      "id": "obs-camilla-g41-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 67,
      "groupId": "science-4",
      "goalId": "goal-41",
      "studentId": "camilla-hovberg"
    },
    {
      "id": "obs-camilla-g41-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 58,
      "groupId": "science-4",
      "goalId": "goal-41",
      "studentId": "camilla-hovberg"
    },

    // Anders Solberg - goal-05 - increasing pattern
    {
      "id": "obs-anders-g05-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 10,
      "groupId": "4A",
      "goalId": "goal-05",
      "studentId": "anders-solberg"
    },
    {
      "id": "obs-anders-g05-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 24,
      "groupId": "4A",
      "goalId": "goal-05",
      "studentId": "anders-solberg"
    },
    {
      "id": "obs-anders-g05-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 37,
      "groupId": "4A",
      "goalId": "goal-05",
      "studentId": "anders-solberg"
    },
    {
      "id": "obs-anders-g05-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 52,
      "groupId": "4A",
      "goalId": "goal-05",
      "studentId": "anders-solberg"
    },
    {
      "id": "obs-anders-g05-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 68,
      "groupId": "4A",
      "goalId": "goal-05",
      "studentId": "anders-solberg"
    },
    {
      "id": "obs-anders-g05-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 83,
      "groupId": "4A",
      "goalId": "goal-05",
      "studentId": "anders-solberg"
    },
    {
      "id": "obs-anders-g05-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 95,
      "groupId": "4A",
      "goalId": "goal-05",
      "studentId": "anders-solberg"
    },

    // Anders Solberg - goal-13 - flat pattern
    {
      "id": "obs-anders-g13-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 58,
      "groupId": "norwegian-4",
      "goalId": "goal-13",
      "studentId": "anders-solberg"
    },
    {
      "id": "obs-anders-g13-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 62,
      "groupId": "norwegian-4",
      "goalId": "goal-13",
      "studentId": "anders-solberg"
    },
    {
      "id": "obs-anders-g13-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 57,
      "groupId": "norwegian-4",
      "goalId": "goal-13",
      "studentId": "anders-solberg"
    },
    {
      "id": "obs-anders-g13-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 60,
      "groupId": "norwegian-4",
      "goalId": "goal-13",
      "studentId": "anders-solberg"
    },
    {
      "id": "obs-anders-g13-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 61,
      "groupId": "norwegian-4",
      "goalId": "goal-13",
      "studentId": "anders-solberg"
    },
    {
      "id": "obs-anders-g13-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 63,
      "groupId": "norwegian-4",
      "goalId": "goal-13",
      "studentId": "anders-solberg"
    },
    {
      "id": "obs-anders-g13-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 60,
      "groupId": "norwegian-4",
      "goalId": "goal-13",
      "studentId": "anders-solberg"
    },

    // Anders Solberg - goal-32 - decreasing pattern
    {
      "id": "obs-anders-g32-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 84,
      "groupId": "english-4",
      "goalId": "goal-32",
      "studentId": "anders-solberg"
    },
    {
      "id": "obs-anders-g32-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 78,
      "groupId": "english-4",
      "goalId": "goal-32",
      "studentId": "anders-solberg"
    },
    {
      "id": "obs-anders-g32-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 71,
      "groupId": "english-4",
      "goalId": "goal-32",
      "studentId": "anders-solberg"
    },
    {
      "id": "obs-anders-g32-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 65,
      "groupId": "english-4",
      "goalId": "goal-32",
      "studentId": "anders-solberg"
    },
    {
      "id": "obs-anders-g32-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 58,
      "groupId": "english-4",
      "goalId": "goal-32",
      "studentId": "anders-solberg"
    },
    {
      "id": "obs-anders-g32-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 52,
      "groupId": "english-4",
      "goalId": "goal-32",
      "studentId": "anders-solberg"
    },
    {
      "id": "obs-anders-g32-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 45,
      "groupId": "english-4",
      "goalId": "goal-32",
      "studentId": "anders-solberg"
    },

    // Tony Lupin - goal-51 - increasing pattern (5th grade - 9 observations)
    {
      "id": "obs-tony-g51-1",
      "createdAt": "2020-06-15T10:00:00Z",
      "masteryValue": 12,
      "groupId": "5A",
      "goalId": "goal-51",
      "studentId": "tony-lupin"
    },
    {
      "id": "obs-tony-g51-2",
      "createdAt": "2021-01-20T10:00:00Z",
      "masteryValue": 23,
      "groupId": "5A",
      "goalId": "goal-51",
      "studentId": "tony-lupin"
    },
    {
      "id": "obs-tony-g51-3",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 35,
      "groupId": "5A",
      "goalId": "goal-51",
      "studentId": "tony-lupin"
    },
    {
      "id": "obs-tony-g51-4",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 48,
      "groupId": "5A",
      "goalId": "goal-51",
      "studentId": "tony-lupin"
    },
    {
      "id": "obs-tony-g51-5",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 60,
      "groupId": "5A",
      "goalId": "goal-51",
      "studentId": "tony-lupin"
    },
    {
      "id": "obs-tony-g51-6",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 72,
      "groupId": "5A",
      "goalId": "goal-51",
      "studentId": "tony-lupin"
    },
    {
      "id": "obs-tony-g51-7",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 83,
      "groupId": "5A",
      "goalId": "goal-51",
      "studentId": "tony-lupin"
    },
    {
      "id": "obs-tony-g51-8",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 91,
      "groupId": "5A",
      "goalId": "goal-51",
      "studentId": "tony-lupin"
    },
    {
      "id": "obs-tony-g51-9",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 98,
      "groupId": "5A",
      "goalId": "goal-51",
      "studentId": "tony-lupin"
    },

    // Tony Lupin - goal-61 - flat pattern (5th grade - 9 observations)
    {
      "id": "obs-tony-g61-1",
      "createdAt": "2020-06-15T10:00:00Z",
      "masteryValue": 54,
      "groupId": "norwegian-5",
      "goalId": "goal-61",
      "studentId": "tony-lupin"
    },
    {
      "id": "obs-tony-g61-2",
      "createdAt": "2021-01-20T10:00:00Z",
      "masteryValue": 56,
      "groupId": "norwegian-5",
      "goalId": "goal-61",
      "studentId": "tony-lupin"
    },
    {
      "id": "obs-tony-g61-3",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 53,
      "groupId": "norwegian-5",
      "goalId": "goal-61",
      "studentId": "tony-lupin"
    },
    {
      "id": "obs-tony-g61-4",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 55,
      "groupId": "norwegian-5",
      "goalId": "goal-61",
      "studentId": "tony-lupin"
    },
    {
      "id": "obs-tony-g61-5",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 57,
      "groupId": "norwegian-5",
      "goalId": "goal-61",
      "studentId": "tony-lupin"
    },
    {
      "id": "obs-tony-g61-6",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 54,
      "groupId": "norwegian-5",
      "goalId": "goal-61",
      "studentId": "tony-lupin"
    },
    {
      "id": "obs-tony-g61-7",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 56,
      "groupId": "norwegian-5",
      "goalId": "goal-61",
      "studentId": "tony-lupin"
    },
    {
      "id": "obs-tony-g61-8",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 58,
      "groupId": "norwegian-5",
      "goalId": "goal-61",
      "studentId": "tony-lupin"
    },
    {
      "id": "obs-tony-g61-9",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 55,
      "groupId": "norwegian-5",
      "goalId": "goal-61",
      "studentId": "tony-lupin"
    },

    // Tony Lupin - goal-71 - erratic pattern (5th grade - 9 observations)
    {
      "id": "obs-tony-g71-1",
      "createdAt": "2020-06-15T10:00:00Z",
      "masteryValue": 38,
      "groupId": "math-5",
      "goalId": "goal-71",
      "studentId": "tony-lupin"
    },
    {
      "id": "obs-tony-g71-2",
      "createdAt": "2021-01-20T10:00:00Z",
      "masteryValue": 62,
      "groupId": "math-5",
      "goalId": "goal-71",
      "studentId": "tony-lupin"
    },
    {
      "id": "obs-tony-g71-3",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 47,
      "groupId": "math-5",
      "goalId": "goal-71",
      "studentId": "tony-lupin"
    },
    {
      "id": "obs-tony-g71-4",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 68,
      "groupId": "math-5",
      "goalId": "goal-71",
      "studentId": "tony-lupin"
    },
    {
      "id": "obs-tony-g71-5",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 53,
      "groupId": "math-5",
      "goalId": "goal-71",
      "studentId": "tony-lupin"
    },
    {
      "id": "obs-tony-g71-6",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 72,
      "groupId": "math-5",
      "goalId": "goal-71",
      "studentId": "tony-lupin"
    },
    {
      "id": "obs-tony-g71-7",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 64,
      "groupId": "math-5",
      "goalId": "goal-71",
      "studentId": "tony-lupin"
    },
    {
      "id": "obs-tony-g71-8",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 79,
      "groupId": "math-5",
      "goalId": "goal-71",
      "studentId": "tony-lupin"
    },
    {
      "id": "obs-tony-g71-9",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 71,
      "groupId": "math-5",
      "goalId": "goal-71",
      "studentId": "tony-lupin"
    },

    // Sara Kahn - goal-72 - increasing pattern (completing her set)
    {
      "id": "obs-sara-g72-1",
      "createdAt": "2020-06-15T10:00:00Z",
      "masteryValue": 18,
      "groupId": "math-5",
      "goalId": "goal-72",
      "studentId": "sara-kahn"
    },
    {
      "id": "obs-sara-g72-2",
      "createdAt": "2021-01-20T10:00:00Z",
      "masteryValue": 29,
      "groupId": "math-5",
      "goalId": "goal-72",
      "studentId": "sara-kahn"
    },
    {
      "id": "obs-sara-g72-3",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 42,
      "groupId": "math-5",
      "goalId": "goal-72",
      "studentId": "sara-kahn"
    },
    {
      "id": "obs-sara-g72-4",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 53,
      "groupId": "math-5",
      "goalId": "goal-72",
      "studentId": "sara-kahn"
    },
    {
      "id": "obs-sara-g72-5",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 67,
      "groupId": "math-5",
      "goalId": "goal-72",
      "studentId": "sara-kahn"
    },
    {
      "id": "obs-sara-g72-6",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 79,
      "groupId": "math-5",
      "goalId": "goal-72",
      "studentId": "sara-kahn"
    },
    {
      "id": "obs-sara-g72-7",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 85,
      "groupId": "math-5",
      "goalId": "goal-72",
      "studentId": "sara-kahn"
    },
    {
      "id": "obs-sara-g72-8",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 92,
      "groupId": "math-5",
      "goalId": "goal-72",
      "studentId": "sara-kahn"
    },
    {
      "id": "obs-sara-g72-9",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 96,
      "groupId": "math-5",
      "goalId": "goal-72",
      "studentId": "sara-kahn"
    },

    // Sara Kahn - goal-81 - erratic pattern
    {
      "id": "obs-sara-g81-1",
      "createdAt": "2020-06-15T10:00:00Z",
      "masteryValue": 34,
      "groupId": "english-5",
      "goalId": "goal-81",
      "studentId": "sara-kahn"
    },
    {
      "id": "obs-sara-g81-2",
      "createdAt": "2021-01-20T10:00:00Z",
      "masteryValue": 52,
      "groupId": "english-5",
      "goalId": "goal-81",
      "studentId": "sara-kahn"
    },
    {
      "id": "obs-sara-g81-3",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 45,
      "groupId": "english-5",
      "goalId": "goal-81",
      "studentId": "sara-kahn"
    },
    {
      "id": "obs-sara-g81-4",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 67,
      "groupId": "english-5",
      "goalId": "goal-81",
      "studentId": "sara-kahn"
    },
    {
      "id": "obs-sara-g81-5",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 58,
      "groupId": "english-5",
      "goalId": "goal-81",
      "studentId": "sara-kahn"
    },
    {
      "id": "obs-sara-g81-6",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 73,
      "groupId": "english-5",
      "goalId": "goal-81",
      "studentId": "sara-kahn"
    },
    {
      "id": "obs-sara-g81-7",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 65,
      "groupId": "english-5",
      "goalId": "goal-81",
      "studentId": "sara-kahn"
    },
    {
      "id": "obs-sara-g81-8",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 81,
      "groupId": "english-5",
      "goalId": "goal-81",
      "studentId": "sara-kahn"
    },
    {
      "id": "obs-sara-g81-9",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 76,
      "groupId": "english-5",
      "goalId": "goal-81",
      "studentId": "sara-kahn"
    },

    // Markus Berg - goal-06 - increasing pattern
    {
      "id": "obs-markus-g06-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 17,
      "groupId": "4A",
      "goalId": "goal-06",
      "studentId": "markus-berg"
    },
    {
      "id": "obs-markus-g06-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 31,
      "groupId": "4A",
      "goalId": "goal-06",
      "studentId": "markus-berg"
    },
    {
      "id": "obs-markus-g06-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 46,
      "groupId": "4A",
      "goalId": "goal-06",
      "studentId": "markus-berg"
    },
    {
      "id": "obs-markus-g06-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 59,
      "groupId": "4A",
      "goalId": "goal-06",
      "studentId": "markus-berg"
    },
    {
      "id": "obs-markus-g06-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 72,
      "groupId": "4A",
      "goalId": "goal-06",
      "studentId": "markus-berg"
    },
    {
      "id": "obs-markus-g06-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 86,
      "groupId": "4A",
      "goalId": "goal-06",
      "studentId": "markus-berg"
    },
    {
      "id": "obs-markus-g06-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 95,
      "groupId": "4A",
      "goalId": "goal-06",
      "studentId": "markus-berg"
    },
    {
      "id": "obs-markus-g06-8",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 90,
      "groupId": "4A",
      "goalId": "goal-06",
      "studentId": "markus-berg"
    },
    {
      "id": "obs-markus-g06-9",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 95,
      "groupId": "4A",
      "goalId": "goal-06",
      "studentId": "markus-berg"
    },

    // Erik Olsen - goal-53 - decreasing pattern
    {
      "id": "obs-erik-g53-1",
      "createdAt": "2020-06-15T10:00:00Z",
      "masteryValue": 92,
      "groupId": "5A",
      "goalId": "goal-53",
      "studentId": "erik-olsen"
    },
    {
      "id": "obs-erik-g53-2",
      "createdAt": "2021-01-20T10:00:00Z",
      "masteryValue": 87,
      "groupId": "5A",
      "goalId": "goal-53",
      "studentId": "erik-olsen"
    },
    {
      "id": "obs-erik-g53-3",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 83,
      "groupId": "5A",
      "goalId": "goal-53",
      "studentId": "erik-olsen"
    },
    {
      "id": "obs-erik-g53-4",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 76,
      "groupId": "5A",
      "goalId": "goal-53",
      "studentId": "erik-olsen"
    },
    {
      "id": "obs-erik-g53-5",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 68,
      "groupId": "5A",
      "goalId": "goal-53",
      "studentId": "erik-olsen"
    },
    {
      "id": "obs-erik-g53-6",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 61,
      "groupId": "5A",
      "goalId": "goal-53",
      "studentId": "erik-olsen"
    },
    {
      "id": "obs-erik-g53-7",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 52,
      "groupId": "5A",
      "goalId": "goal-53",
      "studentId": "erik-olsen"
    },
    {
      "id": "obs-erik-g53-8",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 43,
      "groupId": "5A",
      "goalId": "goal-53",
      "studentId": "erik-olsen"
    },
    {
      "id": "obs-erik-g53-9",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 35,
      "groupId": "5A",
      "goalId": "goal-53",
      "studentId": "erik-olsen"
    },
    {
      "id": "obs-erik-g53-10",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 30,
      "groupId": "5A",
      "goalId": "goal-53",
      "studentId": "erik-olsen"
    },
    {
      "id": "obs-erik-g53-11",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 25,
      "groupId": "5A",
      "goalId": "goal-53",
      "studentId": "erik-olsen"
    },

    // Example for a flat masteryValue pattern
    {
      "id": "obs-linnea-g56-8",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 60,
      "groupId": "5B",
      "goalId": "goal-56",
      "studentId": "linnea-strand"
    },
    {
      "id": "obs-linnea-g56-9",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 60,
      "groupId": "5B",
      "goalId": "goal-56",
      "studentId": "linnea-strand"
    },

    // Example for an erratic masteryValue pattern
    {
      "id": "obs-jakob-g57-8",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 45,
      "groupId": "5B",
      "goalId": "goal-57",
      "studentId": "jakob-dahl"
    },
    {
      "id": "obs-jakob-g57-9",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 50,
      "groupId": "5B",
      "goalId": "goal-57",
      "studentId": "jakob-dahl"
    },
    // Markus Berg - goal-23 - flat pattern
    {
      "id": "obs-markus-g23-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 60,
      "groupId": "math-4",
      "goalId": "goal-23",
      "studentId": "markus-berg"
    },
    {
      "id": "obs-markus-g23-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 62,
      "groupId": "math-4",
      "goalId": "goal-23",
      "studentId": "markus-berg"
    },
    {
      "id": "obs-markus-g23-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 59,
      "groupId": "math-4",
      "goalId": "goal-23",
      "studentId": "markus-berg"
    },
    {
      "id": "obs-markus-g23-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 61,
      "groupId": "math-4",
      "goalId": "goal-23",
      "studentId": "markus-berg"
    },
    {
      "id": "obs-markus-g23-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 63,
      "groupId": "math-4",
      "goalId": "goal-23",
      "studentId": "markus-berg"
    },
    {
      "id": "obs-markus-g23-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 60,
      "groupId": "math-4",
      "goalId": "goal-23",
      "studentId": "markus-berg"
    },
    {
      "id": "obs-markus-g23-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 62,
      "groupId": "math-4",
      "goalId": "goal-23",
      "studentId": "markus-berg"
    },
    // Markus Berg - goal-42 - decreasing pattern
    {
      "id": "obs-markus-g42-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 90,
      "groupId": "science-4",
      "goalId": "goal-42",
      "studentId": "markus-berg"
    },
    {
      "id": "obs-markus-g42-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 85,
      "groupId": "science-4",
      "goalId": "goal-42",
      "studentId": "markus-berg"
    },
    {
      "id": "obs-markus-g42-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 80,
      "groupId": "science-4",
      "goalId": "goal-42",
      "studentId": "markus-berg"
    },
    {
      "id": "obs-markus-g42-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 75,
      "groupId": "science-4",
      "goalId": "goal-42",
      "studentId": "markus-berg"
    },
    {
      "id": "obs-markus-g42-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 70,
      "groupId": "science-4",
      "goalId": "goal-42",
      "studentId": "markus-berg"
    },
    {
      "id": "obs-markus-g42-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 65,
      "groupId": "science-4",
      "goalId": "goal-42",
      "studentId": "markus-berg"
    },
    {
      "id": "obs-markus-g42-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 60,
      "groupId": "science-4",
      "goalId": "goal-42",
      "studentId": "markus-berg"
    },
    // Anders Solberg - goal-05 - increasing pattern
    {
      "id": "obs-anders-g05-8",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 90,
      "groupId": "4A",
      "goalId": "goal-05",
      "studentId": "anders-solberg"
    },
    {
      "id": "obs-anders-g05-9",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 97,
      "groupId": "4A",
      "goalId": "goal-05",
      "studentId": "anders-solberg"
    },
    // Anders Solberg - goal-13 - flat pattern
    {
      "id": "obs-anders-g13-8",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 61,
      "groupId": "norwegian-4",
      "goalId": "goal-13",
      "studentId": "anders-solberg"
    },
    {
      "id": "obs-anders-g13-9",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 63,
      "groupId": "norwegian-4",
      "goalId": "goal-13",
      "studentId": "anders-solberg"
    },
    // Anders Solberg - goal-32 - decreasing pattern
    {
      "id": "obs-anders-g32-8",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 40,
      "groupId": "english-4",
      "goalId": "goal-32",
      "studentId": "anders-solberg"
    },
    {
      "id": "obs-anders-g32-9",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 35,
      "groupId": "english-4",
      "goalId": "goal-32",
      "studentId": "anders-solberg"
    },
    // Emma Pedersen - goal-07 - flat mastery
    {
      "id": "obs-emma-g07-8",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 52,
      "groupId": "4B",
      "goalId": "goal-07",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g07-9",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 51,
      "groupId": "4B",
      "goalId": "goal-07",
      "studentId": "emma-pedersen"
    },
    // Emma Pedersen - goal-14 - increasing mastery
    {
      "id": "obs-emma-g14-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 15,
      "groupId": "norwegian-4",
      "goalId": "goal-14",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g14-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 25,
      "groupId": "norwegian-4",
      "goalId": "goal-14",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g14-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 38,
      "groupId": "norwegian-4",
      "goalId": "goal-14",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g14-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 52,
      "groupId": "norwegian-4",
      "goalId": "goal-14",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g14-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 68,
      "groupId": "norwegian-4",
      "goalId": "goal-14",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g14-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 82,
      "groupId": "norwegian-4",
      "goalId": "goal-14",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g14-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 95,
      "groupId": "norwegian-4",
      "goalId": "goal-14",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g14-8",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 90,
      "groupId": "norwegian-4",
      "goalId": "goal-14",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g14-9",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 95,
      "groupId": "norwegian-4",
      "goalId": "goal-14",
      "studentId": "emma-pedersen"
    },
    // Emma Pedersen - goal-24 - decreasing mastery
    {
      "id": "obs-emma-g24-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 80,
      "groupId": "math-4",
      "goalId": "goal-24",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g24-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 75,
      "groupId": "math-4",
      "goalId": "goal-24",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g24-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 70,
      "groupId": "math-4",
      "goalId": "goal-24",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g24-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 65,
      "groupId": "math-4",
      "goalId": "goal-24",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g24-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 60,
      "groupId": "math-4",
      "goalId": "goal-24",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g24-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 55,
      "groupId": "math-4",
      "goalId": "goal-24",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g24-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 50,
      "groupId": "math-4",
      "goalId": "goal-24",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g24-8",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 45,
      "groupId": "math-4",
      "goalId": "goal-24",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g24-9",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 40,
      "groupId": "math-4",
      "goalId": "goal-24",
      "studentId": "emma-pedersen"
    },
    // Thomas Lie - goal-08 - increasing mastery
    {
      "id": "obs-thomas-g08-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 10,
      "groupId": "4B",
      "goalId": "goal-08",
      "studentId": "thomas-lie"
    },
    {
      "id": "obs-thomas-g08-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 20,
      "groupId": "4B",
      "goalId": "goal-08",
      "studentId": "thomas-lie"
    },
    {
      "id": "obs-thomas-g08-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 35,
      "groupId": "4B",
      "goalId": "goal-08",
      "studentId": "thomas-lie"
    },
    {
      "id": "obs-thomas-g08-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 50,
      "groupId": "4B",
      "goalId": "goal-08",
      "studentId": "thomas-lie"
    },
    {
      "id": "obs-thomas-g08-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 65,
      "groupId": "4B",
      "goalId": "goal-08",
      "studentId": "thomas-lie"
    },
    {
      "id": "obs-thomas-g08-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 80,
      "groupId": "4B",
      "goalId": "goal-08",
      "studentId": "thomas-lie"
    },
    {
      "id": "obs-thomas-g08-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 95,
      "groupId": "4B",
      "goalId": "goal-08",
      "studentId": "thomas-lie"
    },
    {
      "id": "obs-thomas-g08-8",
      "createdAt": "2025-01-20T10:00:00Z",
      "masteryValue": 92,
      "groupId": "4B",
      "goalId": "goal-08",
      "studentId": "thomas-lie"
    },
    {
      "id": "obs-thomas-g08-9",
      "createdAt": "2025-06-15T10:00:00Z",
      "masteryValue": 98,
      "groupId": "4B",
      "goalId": "goal-08",
      "studentId": "thomas-lie"
    },
    // Thomas Lie - goal-15 - flat mastery
    {
      "id": "obs-thomas-g15-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 55,
      "groupId": "norwegian-4",
      "goalId": "goal-15",
      "studentId": "thomas-lie"
    },
    {
      "id": "obs-thomas-g15-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 58,
      "groupId": "norwegian-4",
      "goalId": "goal-15",
      "studentId": "thomas-lie"
    },
    {
      "id": "obs-thomas-g15-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 56,
      "groupId": "norwegian-4",
      "goalId": "goal-15",
      "studentId": "thomas-lie"
    },
    {
      "id": "obs-thomas-g15-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 57,
      "groupId": "norwegian-4",
      "goalId": "goal-15",
      "studentId": "thomas-lie"
    },
    {
      "id": "obs-thomas-g15-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 59,
      "groupId": "norwegian-4",
      "goalId": "goal-15",
      "studentId": "thomas-lie"
    },
    {
      "id": "obs-thomas-g15-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 57,
      "groupId": "norwegian-4",
      "goalId": "goal-15",
      "studentId": "thomas-lie"
    },
    {
      "id": "obs-thomas-g15-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 58,
      "groupId": "norwegian-4",
      "goalId": "goal-15",
      "studentId": "thomas-lie"
    },
    {
      "id": "obs-thomas-g15-8",
      "createdAt": "2025-01-20T10:00:00Z",
      "masteryValue": 59,
      "groupId": "norwegian-4",
      "goalId": "goal-15",
      "studentId": "thomas-lie"
    },
    {
      "id": "obs-thomas-g15-9",
      "createdAt": "2025-06-15T10:00:00Z",
      "masteryValue": 60,
      "groupId": "norwegian-4",
      "goalId": "goal-15",
      "studentId": "thomas-lie"
    },
    // Thomas Lie - goal-25 - decreasing mastery
    {
      "id": "obs-thomas-g25-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 90,
      "groupId": "math-4",
      "goalId": "goal-25",
      "studentId": "thomas-lie"
    },
    {
      "id": "obs-thomas-g25-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 85,
      "groupId": "math-4",
      "goalId": "goal-25",
      "studentId": "thomas-lie"
    },
    {
      "id": "obs-thomas-g25-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 80,
      "groupId": "math-4",
      "goalId": "goal-25",
      "studentId": "thomas-lie"
    },
    {
      "id": "obs-thomas-g25-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 75,
      "groupId": "math-4",
      "goalId": "goal-25",
      "studentId": "thomas-lie"
    },
    {
      "id": "obs-thomas-g25-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 70,
      "groupId": "math-4",
      "goalId": "goal-25",
      "studentId": "thomas-lie"
    },
    {
      "id": "obs-thomas-g25-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 65,
      "groupId": "math-4",
      "goalId": "goal-25",
      "studentId": "thomas-lie"
    },
    {
      "id": "obs-thomas-g25-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 60,
      "groupId": "math-4",
      "goalId": "goal-25",
      "studentId": "thomas-lie"
    },
    {
      "id": "obs-thomas-g25-8",
      "createdAt": "2025-01-20T10:00:00Z",
      "masteryValue": 55,
      "groupId": "math-4",
      "goalId": "goal-25",
      "studentId": "thomas-lie"
    },
    {
      "id": "obs-thomas-g25-9",
      "createdAt": "2025-06-15T10:00:00Z",
      "masteryValue": 50,
      "groupId": "math-4",
      "goalId": "goal-25",
      "studentId": "thomas-lie"
    },
    // Sofie Hansen - goal-09 - increasing mastery
    {
      "id": "obs-sofie-g09-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 15,
      "groupId": "4B",
      "goalId": "goal-09",
      "studentId": "sofie-hansen"
    },
    {
      "id": "obs-sofie-g09-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 25,
      "groupId": "4B",
      "goalId": "goal-09",
      "studentId": "sofie-hansen"
    },
    {
      "id": "obs-sofie-g09-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 38,
      "groupId": "4B",
      "goalId": "goal-09",
      "studentId": "sofie-hansen"
    },
    {
      "id": "obs-sofie-g09-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 52,
      "groupId": "4B",
      "goalId": "goal-09",
      "studentId": "sofie-hansen"
    },
    {
      "id": "obs-sofie-g09-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 68,
      "groupId": "4B",
      "goalId": "goal-09",
      "studentId": "sofie-hansen"
    },
    {
      "id": "obs-sofie-g09-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 82,
      "groupId": "4B",
      "goalId": "goal-09",
      "studentId": "sofie-hansen"
    },
    {
      "id": "obs-sofie-g09-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 95,
      "groupId": "4B",
      "goalId": "goal-09",
      "studentId": "sofie-hansen"
    },
    {
      "id": "obs-sofie-g09-8",
      "createdAt": "2025-01-20T10:00:00Z",
      "masteryValue": 92,
      "groupId": "4B",
      "goalId": "goal-09",
      "studentId": "sofie-hansen"
    },
    {
      "id": "obs-sofie-g09-9",
      "createdAt": "2025-06-15T10:00:00Z",
      "masteryValue": 98,
      "groupId": "4B",
      "goalId": "goal-09",
      "studentId": "sofie-hansen"
    },
    // Sofie Hansen - goal-34 - flat mastery
    {
      "id": "obs-sofie-g34-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 55,
      "groupId": "english-4",
      "goalId": "goal-34",
      "studentId": "sofie-hansen"
    },
    {
      "id": "obs-sofie-g34-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 58,
      "groupId": "english-4",
      "goalId": "goal-34",
      "studentId": "sofie-hansen"
    },
    {
      "id": "obs-sofie-g34-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 56,
      "groupId": "english-4",
      "goalId": "goal-34",
      "studentId": "sofie-hansen"
    },
    {
      "id": "obs-sofie-g34-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 57,
      "groupId": "english-4",
      "goalId": "goal-34",
      "studentId": "sofie-hansen"
    },
    {
      "id": "obs-sofie-g34-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 59,
      "groupId": "english-4",
      "goalId": "goal-34",
      "studentId": "sofie-hansen"
    },
    {
      "id": "obs-sofie-g34-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 57,
      "groupId": "english-4",
      "goalId": "goal-34",
      "studentId": "sofie-hansen"
    },
    {
      "id": "obs-sofie-g34-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 58,
      "groupId": "english-4",
      "goalId": "goal-34",
      "studentId": "sofie-hansen"
    },
    {
      "id": "obs-sofie-g34-8",
      "createdAt": "2025-01-20T10:00:00Z",
      "masteryValue": 59,
      "groupId": "english-4",
      "goalId": "goal-34",
      "studentId": "sofie-hansen"
    },
    {
      "id": "obs-sofie-g34-9",
      "createdAt": "2025-06-15T10:00:00Z",
      "masteryValue": 60,
      "groupId": "english-4",
      "goalId": "goal-34",
      "studentId": "sofie-hansen"
    },
    // Sofie Hansen - goal-44 - decreasing mastery
    {
      "id": "obs-sofie-g44-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 90,
      "groupId": "science-4",
      "goalId": "goal-44",
      "studentId": "sofie-hansen"
    },
    {
      "id": "obs-sofie-g44-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 85,
      "groupId": "science-4",
      "goalId": "goal-44",
      "studentId": "sofie-hansen"
    },
    {
      "id": "obs-sofie-g44-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 80,
      "groupId": "science-4",
      "goalId": "goal-44",
      "studentId": "sofie-hansen"
    },
    {
      "id": "obs-sofie-g44-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 75,
      "groupId": "science-4",
      "goalId": "goal-44",
      "studentId": "sofie-hansen"
    },
    {
      "id": "obs-sofie-g44-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 70,
      "groupId": "science-4",
      "goalId": "goal-44",
      "studentId": "sofie-hansen"
    },
    {
      "id": "obs-sofie-g44-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 65,
      "groupId": "science-4",
      "goalId": "goal-44",
      "studentId": "sofie-hansen"
    },
    {
      "id": "obs-sofie-g44-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 60,
      "groupId": "science-4",
      "goalId": "goal-44",
      "studentId": "sofie-hansen"
    },
    {
      "id": "obs-sofie-g44-8",
      "createdAt": "2025-01-20T10:00:00Z",
      "masteryValue": 55,
      "groupId": "science-4",
      "goalId": "goal-44",
      "studentId": "sofie-hansen"
    },
    {
      "id": "obs-sofie-g44-9",
      "createdAt": "2025-06-15T10:00:00Z",
      "masteryValue": 50,
      "groupId": "science-4",
      "goalId": "goal-44",
      "studentId": "sofie-hansen"
    },
    // Emma Pedersen - goal-33 - erratic mastery
    {
      "id": "obs-emma-g33-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 35,
      "groupId": "english-4",
      "goalId": "goal-33",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g33-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 58,
      "groupId": "english-4",
      "goalId": "goal-33",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g33-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 42,
      "groupId": "english-4",
      "goalId": "goal-33",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g33-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 75,
      "groupId": "english-4",
      "goalId": "goal-33",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g33-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 65,
      "groupId": "english-4",
      "goalId": "goal-33",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g33-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 82,
      "groupId": "english-4",
      "goalId": "goal-33",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g33-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 68,
      "groupId": "english-4",
      "goalId": "goal-33",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g33-8",
      "createdAt": "2025-01-20T10:00:00Z",
      "masteryValue": 85,
      "groupId": "english-4",
      "goalId": "goal-33",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g33-9",
      "createdAt": "2025-06-15T10:00:00Z",
      "masteryValue": 72,
      "groupId": "english-4",
      "goalId": "goal-33",
      "studentId": "emma-pedersen"
    },
    // Emma Pedersen - goal-43 - decreasing mastery
    {
      "id": "obs-emma-g43-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 80,
      "groupId": "science-4",
      "goalId": "goal-43",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g43-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 75,
      "groupId": "science-4",
      "goalId": "goal-43",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g43-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 70,
      "groupId": "science-4",
      "goalId": "goal-43",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g43-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 65,
      "groupId": "science-4",
      "goalId": "goal-43",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g43-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 60,
      "groupId": "science-4",
      "goalId": "goal-43",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g43-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 55,
      "groupId": "science-4",
      "goalId": "goal-43",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g43-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 50,
      "groupId": "science-4",
      "goalId": "goal-43",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g43-8",
      "createdAt": "2025-01-20T10:00:00Z",
      "masteryValue": 45,
      "groupId": "science-4",
      "goalId": "goal-43",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g43-9",
      "createdAt": "2025-06-15T10:00:00Z",
      "masteryValue": 40,
      "groupId": "science-4",
      "goalId": "goal-43",
      "studentId": "emma-pedersen"
    },
    // Jonas Johansen - goal-09 - increasing mastery
    {
      "id": "obs-jonas-g09-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 15,
      "groupId": "4B",
      "goalId": "goal-09",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g09-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 25,
      "groupId": "4B",
      "goalId": "goal-09",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g09-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 38,
      "groupId": "4B",
      "goalId": "goal-09",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g09-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 52,
      "groupId": "4B",
      "goalId": "goal-09",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g09-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 68,
      "groupId": "4B",
      "goalId": "goal-09",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g09-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 82,
      "groupId": "4B",
      "goalId": "goal-09",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g09-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 95,
      "groupId": "4B",
      "goalId": "goal-09",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g09-8",
      "createdAt": "2025-01-20T10:00:00Z",
      "masteryValue": 92,
      "groupId": "4B",
      "goalId": "goal-09",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g09-9",
      "createdAt": "2025-06-15T10:00:00Z",
      "masteryValue": 98,
      "groupId": "4B",
      "goalId": "goal-09",
      "studentId": "jonas-johansen"
    },
    // Jonas Johansen - goal-16 - flat mastery
    {
      "id": "obs-jonas-g16-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 55,
      "groupId": "norwegian-4",
      "goalId": "goal-16",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g16-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 58,
      "groupId": "norwegian-4",
      "goalId": "goal-16",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g16-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 56,
      "groupId": "norwegian-4",
      "goalId": "goal-16",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g16-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 57,
      "groupId": "norwegian-4",
      "goalId": "goal-16",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g16-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 59,
      "groupId": "norwegian-4",
      "goalId": "goal-16",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g16-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 57,
      "groupId": "norwegian-4",
      "goalId": "goal-16",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g16-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 58,
      "groupId": "norwegian-4",
      "goalId": "goal-16",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g16-8",
      "createdAt": "2025-01-20T10:00:00Z",
      "masteryValue": 59,
      "groupId": "norwegian-4",
      "goalId": "goal-16",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g16-9",
      "createdAt": "2025-06-15T10:00:00Z",
      "masteryValue": 60,
      "groupId": "norwegian-4",
      "goalId": "goal-16",
      "studentId": "jonas-johansen"
    },
    // Jonas Johansen - goal-35 - decreasing mastery
    {
      "id": "obs-jonas-g35-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 90,
      "groupId": "english-4",
      "goalId": "goal-35",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g35-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 85,
      "groupId": "english-4",
      "goalId": "goal-35",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g35-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 80,
      "groupId": "english-4",
      "goalId": "goal-35",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g35-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 75,
      "groupId": "english-4",
      "goalId": "goal-35",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g35-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 70,
      "groupId": "english-4",
      "goalId": "goal-35",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g35-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 65,
      "groupId": "english-4",
      "goalId": "goal-35",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g35-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 60,
      "groupId": "english-4",
      "goalId": "goal-35",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g35-8",
      "createdAt": "2025-01-20T10:00:00Z",
      "masteryValue": 55,
      "groupId": "english-4",
      "goalId": "goal-35",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g35-9",
      "createdAt": "2025-06-15T10:00:00Z",
      "masteryValue": 50,
      "groupId": "english-4",
      "goalId": "goal-35",
      "studentId": "jonas-johansen"
    },
    // Jonas Johansen - goal-45 - erratic mastery
    {
      "id": "obs-jonas-g45-1",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 35,
      "groupId": "science-4",
      "goalId": "goal-45",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g45-2",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 58,
      "groupId": "science-4",
      "goalId": "goal-45",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g45-3",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 42,
      "groupId": "science-4",
      "goalId": "goal-45",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g45-4",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 75,
      "groupId": "science-4",
      "goalId": "goal-45",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g45-5",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 65,
      "groupId": "science-4",
      "goalId": "goal-45",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g45-6",
      "createdAt": "2024-01-20T10:00:00Z",
      "masteryValue": 82,
      "groupId": "science-4",
      "goalId": "goal-45",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g45-7",
      "createdAt": "2024-06-15T10:00:00Z",
      "masteryValue": 68,
      "groupId": "science-4",
      "goalId": "goal-45",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g45-8",
      "createdAt": "2025-01-20T10:00:00Z",
      "masteryValue": 85,
      "groupId": "science-4",
      "goalId": "goal-45",
      "studentId": "jonas-johansen"
    },
    {
      "id": "obs-jonas-g45-9",
      "createdAt": "2025-06-15T10:00:00Z",
      "masteryValue": 72,
      "groupId": "science-4",
      "goalId": "goal-45",
      "studentId": "jonas-johansen"
    },
    // Sofie Hansen - goal-09 - increasing mastery
    {
      "id": "obs-sofie-g09-10",
      "createdAt": "2026-01-20T10:00:00Z",
      "masteryValue": 92,
      "groupId": "4B",
      "goalId": "goal-09",
      "studentId": "sofie-hansen"
    },
    {
      "id": "obs-sofie-g09-11",
      "createdAt": "2026-06-15T10:00:00Z",
      "masteryValue": 98,
      "groupId": "4B",
      "goalId": "goal-09",
      "studentId": "sofie-hansen"
    },
    // Sofie Hansen - goal-34 - flat mastery
    {
      "id": "obs-sofie-g34-10",
      "createdAt": "2026-01-20T10:00:00Z",
      "masteryValue": 59,
      "groupId": "english-4",
      "goalId": "goal-34",
      "studentId": "sofie-hansen"
    },
    {
      "id": "obs-sofie-g34-11",
      "createdAt": "2026-06-15T10:00:00Z",
      "masteryValue": 60,
      "groupId": "english-4",
      "goalId": "goal-34",
      "studentId": "sofie-hansen"
    },
    // Sofie Hansen - goal-44 - decreasing mastery
    {
      "id": "obs-sofie-g44-10",
      "createdAt": "2026-01-20T10:00:00Z",
      "masteryValue": 55,
      "groupId": "science-4",
      "goalId": "goal-44",
      "studentId": "sofie-hansen"
    },
    {
      "id": "obs-sofie-g44-11",
      "createdAt": "2026-06-15T10:00:00Z",
      "masteryValue": 50,
      "groupId": "science-4",
      "goalId": "goal-44",
      "studentId": "sofie-hansen"
    },
    // Emma Pedersen - goal-33 - erratic mastery
    {
      "id": "obs-emma-g33-10",
      "createdAt": "2026-01-20T10:00:00Z",
      "masteryValue": 85,
      "groupId": "english-4",
      "goalId": "goal-33",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g33-11",
      "createdAt": "2026-06-15T10:00:00Z",
      "masteryValue": 72,
      "groupId": "english-4",
      "goalId": "goal-33",
      "studentId": "emma-pedersen"
    },
    // Emma Pedersen - goal-43 - decreasing mastery
    {
      "id": "obs-emma-g43-10",
      "createdAt": "2026-01-20T10:00:00Z",
      "masteryValue": 45,
      "groupId": "science-4",
      "goalId": "goal-43",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g43-11",
      "createdAt": "2026-06-15T10:00:00Z",
      "masteryValue": 40,
      "groupId": "science-4",
      "goalId": "goal-43",
      "studentId": "emma-pedersen"
    },
    // Emma Pedersen - goal-07 - flat mastery
    {
      "id": "obs-emma-g07-10",
      "createdAt": "2026-01-20T10:00:00Z",
      "masteryValue": 52,
      "groupId": "4B",
      "goalId": "goal-07",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g07-11",
      "createdAt": "2026-06-15T10:00:00Z",
      "masteryValue": 51,
      "groupId": "4B",
      "goalId": "goal-07",
      "studentId": "emma-pedersen"
    },
    // Emma Pedersen - goal-14 - increasing mastery
    {
      "id": "obs-emma-g14-10",
      "createdAt": "2026-01-20T10:00:00Z",
      "masteryValue": 90,
      "groupId": "norwegian-4",
      "goalId": "goal-14",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g14-11",
      "createdAt": "2026-06-15T10:00:00Z",
      "masteryValue": 95,
      "groupId": "norwegian-4",
      "goalId": "goal-14",
      "studentId": "emma-pedersen"
    },
    // Emma Pedersen - goal-24 - decreasing mastery
    {
      "id": "obs-emma-g24-10",
      "createdAt": "2026-01-20T10:00:00Z",
      "masteryValue": 45,
      "groupId": "math-4",
      "goalId": "goal-24",
      "studentId": "emma-pedersen"
    },
    {
      "id": "obs-emma-g24-11",
      "createdAt": "2026-06-15T10:00:00Z",
      "masteryValue": 40,
      "groupId": "math-4",
      "goalId": "goal-24",
      "studentId": "emma-pedersen"
    },
    // Thomas Lie - goal-08 - increasing mastery
    {
      "id": "obs-thomas-g08-10",
      "createdAt": "2026-01-20T10:00:00Z",
      "masteryValue": 92,
      "groupId": "4B",
      "goalId": "goal-08",
      "studentId": "thomas-lie"
    },
    {
      "id": "obs-thomas-g08-11",
      "createdAt": "2026-06-15T10:00:00Z",
      "masteryValue": 98,
      "groupId": "4B",
      "goalId": "goal-08",
      "studentId": "thomas-lie"
    },
    // Thomas Lie - goal-15 - flat mastery
    {
      "id": "obs-thomas-g15-10",
      "createdAt": "2026-01-20T10:00:00Z",
      "masteryValue": 59,
      "groupId": "norwegian-4",
      "goalId": "goal-15",
      "studentId": "thomas-lie"
    },
    {
      "id": "obs-thomas-g15-11",
      "createdAt": "2026-06-15T10:00:00Z",
      "masteryValue": 60,
      "groupId": "norwegian-4",
      "goalId": "goal-15",
      "studentId": "thomas-lie"
    },
    // Thomas Lie - goal-25 - decreasing mastery
    {
      "id": "obs-thomas-g25-10",
      "createdAt": "2026-01-20T10:00:00Z",
      "masteryValue": 55,
      "groupId": "math-4",
      "goalId": "goal-25",
      "studentId": "thomas-lie"
    },
    {
      "id": "obs-thomas-g25-11",
      "createdAt": "2026-06-15T10:00:00Z",
      "masteryValue": 50,
      "groupId": "math-4",
      "goalId": "goal-25",
      "studentId": "thomas-lie"
    },
    // Erik Olsen - goal-82 - increasing mastery
    {
      "id": "obs-erik-g82-1",
      "createdAt": "2020-06-15T10:00:00Z",
      "masteryValue": 20,
      "groupId": "english-5",
      "goalId": "goal-82",
      "studentId": "erik-olsen"
    },
    {
      "id": "obs-erik-g82-2",
      "createdAt": "2021-01-20T10:00:00Z",
      "masteryValue": 35,
      "groupId": "english-5",
      "goalId": "goal-82",
      "studentId": "erik-olsen"
    },
    {
      "id": "obs-erik-g82-3",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 48,
      "groupId": "english-5",
      "goalId": "goal-82",
      "studentId": "erik-olsen"
    },
    {
      "id": "obs-erik-g82-4",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 62,
      "groupId": "english-5",
      "goalId": "goal-82",
      "studentId": "erik-olsen"
    },
    {
      "id": "obs-erik-g82-5",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 75,
      "groupId": "english-5",
      "goalId": "goal-82",
      "studentId": "erik-olsen"
    },
    {
      "id": "obs-erik-g82-6",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 85,
      "groupId": "english-5",
      "goalId": "goal-82",
      "studentId": "erik-olsen"
    },
    {
      "id": "obs-erik-g82-7",
      "createdAt": "2023-06-15T10:00:00Z",
      "masteryValue": 92,
      "groupId": "english-5",
      "goalId": "goal-82",
      "studentId": "erik-olsen"
    },

    // Hanna Nilsen - goal-54 - erratic pattern
    {
      "id": "obs-hanna-g54-1",
      "createdAt": "2020-06-15T10:00:00Z",
      "masteryValue": 45,
      "groupId": "5A",
      "goalId": "goal-54",
      "studentId": "hanna-nilsen"
    },
    {
      "id": "obs-hanna-g54-2",
      "createdAt": "2021-01-20T10:00:00Z",
      "masteryValue": 68,
      "groupId": "5A",
      "goalId": "goal-54",
      "studentId": "hanna-nilsen"
    },
    {
      "id": "obs-hanna-g54-3",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 52,
      "groupId": "5A",
      "goalId": "goal-54",
      "studentId": "hanna-nilsen"
    },
    {
      "id": "obs-hanna-g54-4",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 78,
      "groupId": "5A",
      "goalId": "goal-54",
      "studentId": "hanna-nilsen"
    },
    {
      "id": "obs-hanna-g54-5",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 65,
      "groupId": "5A",
      "goalId": "goal-54",
      "studentId": "hanna-nilsen"
    },

    // Mats Bakken - goal-73 - flat pattern 
    {
      "id": "obs-mats-g73-1",
      "createdAt": "2020-06-15T10:00:00Z",
      "masteryValue": 60,
      "groupId": "math-5",
      "goalId": "goal-73",
      "studentId": "mats-bakken"
    },
    {
      "id": "obs-mats-g73-2",
      "createdAt": "2021-01-20T10:00:00Z",
      "masteryValue": 62,
      "groupId": "math-5",
      "goalId": "goal-73",
      "studentId": "mats-bakken"
    },
    {
      "id": "obs-mats-g73-3",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 58,
      "groupId": "math-5",
      "goalId": "goal-73",
      "studentId": "mats-bakken"
    },
    {
      "id": "obs-mats-g73-4",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 61,
      "groupId": "math-5",
      "goalId": "goal-73",
      "studentId": "mats-bakken"
    },

    // Linnea Strand - goal-64 - decreasing pattern
    {
      "id": "obs-linnea-g64-1",
      "createdAt": "2020-06-15T10:00:00Z",
      "masteryValue": 85,
      "groupId": "norwegian-5",
      "goalId": "goal-64",
      "studentId": "linnea-strand"
    },
    {
      "id": "obs-linnea-g64-2",
      "createdAt": "2021-01-20T10:00:00Z",
      "masteryValue": 78,
      "groupId": "norwegian-5",
      "goalId": "goal-64",
      "studentId": "linnea-strand"
    },
    {
      "id": "obs-linnea-g64-3",
      "createdAt": "2021-06-15T10:00:00Z",
      "masteryValue": 70,
      "groupId": "norwegian-5",
      "goalId": "goal-64",
      "studentId": "linnea-strand"
    },
    {
      "id": "obs-linnea-g64-4",
      "createdAt": "2022-01-20T10:00:00Z",
      "masteryValue": 62,
      "groupId": "norwegian-5",
      "goalId": "goal-64",
      "studentId": "linnea-strand"
    },
    {
      "id": "obs-linnea-g64-5",
      "createdAt": "2022-06-15T10:00:00Z",
      "masteryValue": 55,
      "groupId": "norwegian-5",
      "goalId": "goal-64",
      "studentId": "linnea-strand"
    },
    {
      "id": "obs-linnea-g64-6",
      "createdAt": "2023-01-20T10:00:00Z",
      "masteryValue": 48,
      "groupId": "norwegian-5",
      "goalId": "goal-64",
      "studentId": "linnea-strand"
    }
  ],
  "masteryLevels": [
    {
      "text": "Mestrer ikke",
      "minValue": 0,
      "maxValue": 20,
      "color": "rgb(229, 50, 43)"
    },
    {
      "text": "Mestrer sjelden",
      "minValue": 21,
      "maxValue": 40,
      "color": "rgb(159, 113, 202)"
    },
    {
      "text": "Mestrer i blant",
      "minValue": 41,
      "maxValue": 60,
      "color": "rgb(86, 174, 232)"
    },
    {
      "text": "Mestrer ofte",
      "minValue": 61,
      "maxValue": 80,
      "color": "rgb(241, 249, 97)"
    },
    {
      "text": "Mestrer",
      "minValue": 81,
      "maxValue": 100,
      "color": "rgb(160, 207, 106)"
    }
  ]
}