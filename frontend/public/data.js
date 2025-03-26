export const data = {
  "students": [
    {
      "id": "pia-eriksen",
      "name": "Pia Eriksen",
      "age": 10,
      "groupId": "5A",
      "goalIds": ["goal-01", "goal-02"],
      "subjectIds": ["norwegian", "math", "english"]
    },
    {
      "id": "camilla-hovberg",
      "name": "Camilla Hovberg",
      "age": 10,
      "groupId": "5A",
      "goalIds": [],
      "subjectIds": ["norwegian", "math"]
    },
    {
      "id": "tony-lupin",
      "name": "Tony Lupin",
      "age": 9,
      "groupId": "3D",
      "goalIds": [],
      "subjectIds": ["norwegian"]
    },
    {
      "id": "frank-larsen",
      "name": "Frank Larsen",
      "age": 13,
      "groupId": "8C",
      "goalIds": [],
      "subjectIds": ["norwegian", "math", "english"]
    }
  ],
  "groups": [
    {
      "id": "5A",
      "name": "5A",
      "grade": 5,
      "section": "A",
      "teacherId": "teacher-01"
    },
    {
      "id": "3D",
      "name": "3D",
      "grade": 3,
      "section": "D",
      "teacherId": "teacher-02"
    },
    {
      "id": "8C",
      "name": "8C",
      "grade": 8,
      "section": "C",
      "teacherId": "teacher-03"
    }
  ],
  "teachers": [
    {
      "id": "teacher-01",
      "name": "Lars Hansen",
      "groupIds": ["5A"]
    },
    {
      "id": "teacher-02",
      "name": "Maria Olsen",
      "groupIds": ["3D"]
    },
    {
      "id": "teacher-03",
      "name": "Jens Pedersen",
      "groupIds": ["8C"]
    }
  ],
  "goals": [
    {
      "id": "goal-01",
      "title": "Telle til 10",
      "description": "Eleven kan telle til 10.",
      "subjectId": "math",
      "masteryLevel": 25,
      "studentId": "pia-eriksen",
      "observationIds": ["obs-pia-01", "obs-pia-02"]
    },
    {
      "id": "goal-02",
      "title": "Kan skrive navnet sitt",
      "description": "Eleven kan skrive navnet sitt med blyant og papir.",
      "subjectId": "norwegian",
      "masteryLevel": 0,
      "studentId": "pia-eriksen",
      "observationIds": ["obs-pia-03", "obs-pia-04"]
    }
  ],
  "observations": [
    {
      "id": "obs-pia-01",
      "date": "2024-06-02",
      "masteryText": "Mestrer litt",
      "subjectId": "math",
      "goalId": "goal-01",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-02",
      "date": "2025-01-19",
      "masteryText": "Mestrer av og til",
      "subjectId": "math",
      "goalId": "goal-01",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-03",
      "date": "2024-06-02",
      "masteryText": "Mestrer ikke",
      "subjectId": "norwegian",
      "goalId": "goal-02",
      "studentId": "pia-eriksen"
    },
    {
      "id": "obs-pia-04",
      "date": "2025-01-20",
      "masteryText": "Mestrer av og til",
      "subjectId": "norwegian",
      "goalId": "goal-02",
      "studentId": "pia-eriksen"
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
  ],
  "subjects": [
    {
      "id": "norwegian",
      "name": "Norsk"
    },
    {
      "id": "math",
      "name": "Matte"
    },
    {
      "id": "english",
      "name": "Engelsk"
    }
  ]
}